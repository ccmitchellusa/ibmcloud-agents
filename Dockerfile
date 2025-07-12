# =============== Builder Stage ===============
FROM registry.access.redhat.com/ubi9-minimal:9.6-1747218906 AS builder
LABEL maintainer="Ryan Edgell" \
      name="ibm/ibmcloud-base-agent-build" \
      description="Builder stage for IBM Cloud Base Agent" \
      version="0.1.0"

# Build arguments
ARG PYTHON_VERSION=3.12

# Install Python and build dependencies
RUN microdnf update -y && \
    microdnf install -y python${PYTHON_VERSION} && \
    microdnf clean all && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1

# Copy uv from the uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Build environment configuration
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/venv \
    UV_PYTHON=/usr/bin/python3

WORKDIR /app

RUN uv venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy dependency files first for better caching
COPY uv.lock pyproject.toml ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev --no-editable

# Copy the source code and build the package
COPY . .
RUN rm -rf /app/.venv && \
    uv build

# =============== Final Runtime Stage ===============
FROM registry.access.redhat.com/ubi9-minimal:9.6-1747218906
LABEL maintainer="Ryan Edgell" \
      name="ibm/ibmcloud-base-agent" \
      description="IBM Cloud Base Agent for automated cloud operations" \
      version="0.1.0"

# Build arguments
ARG PYTHON_VERSION=3.12
ARG IBMCLOUD_VERSION=2.35.0
ARG IBMCLOUD_ARCH=arm64
ARG IBMCLOUD_PLUGINS

# Environment variables
ENV VIRTUAL_ENV=/venv \
    PATH="/$VIRTUAL_ENV/bin:$PATH"

# Install Python and required system packages
RUN microdnf update -y && \
    microdnf install -y python${PYTHON_VERSION} tar gzip && \
    microdnf clean all && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1

# Copy application files from builder
COPY --from=builder /venv /venv
COPY --from=builder /app/dist/*.whl /tmp/
COPY --from=builder /app/start.sh /app/start.sh
COPY --from=builder /app/agent.yaml /app/agent.yaml

# Install the application
RUN chmod +x /app/start.sh && \
    /venv/bin/python3 -m ensurepip --upgrade && \
    /venv/bin/pip3 install /tmp/*.whl && \
    rm -rf /tmp/*.whl

RUN curl -L "https://download.clis.cloud.ibm.com/ibm-cloud-cli/${IBMCLOUD_VERSION}/IBM_Cloud_CLI_${IBMCLOUD_VERSION}_${IBMCLOUD_ARCH}.tar.gz" -o /tmp/ibmcloud.tar.gz && \
    tar -xf /tmp/ibmcloud.tar.gz -C /tmp && \
    mv /tmp/Bluemix_CLI/bin/ibmcloud /usr/local/bin/ && \
    rm -rf /tmp/ibmcloud.tar.gz /tmp/Bluemix_CLI && \
    chmod +x /usr/local/bin/ibmcloud

# Update permissions for non-root user
RUN chown -R 1001:0 /app && \
    chmod -R g=u /app

EXPOSE 8000

WORKDIR /app

# Run as non-root user
USER 1001

# Install IBM Cloud CLI and plugins
RUN if [ -n "${IBMCLOUD_PLUGINS}" ]; then \
        ibmcloud plugin install $IBMCLOUD_PLUGINS -f -q || true; \
    else \
        echo "No specific plugins specified, installing all..." && \
        ibmcloud plugin install --all -f -q || true; \
    fi

CMD ["./start.sh"]
