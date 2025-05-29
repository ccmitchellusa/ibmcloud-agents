# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS uv

# Create a non-root user
RUN useradd -m -u 1000 app

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1 
ENV UV_LINK_MODE=copy 

# Copy dependency files first
COPY uv.lock pyproject.toml /app/
RUN chown -R app:app /app

# Install the project's dependencies using the lockfile and settings
RUN su - app -c "cd /app && uv sync --frozen --no-install-project --no-dev --no-editable"

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app/
RUN chown -R app:app /app && \
    su - app -c "cd /app && uv sync --frozen --no-dev --no-editable"

FROM python:3.13-slim-bookworm

# Create a non-root user
RUN useradd -m -u 1000 app

# Install curl for downloading the IBM Cloud CLI
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Download and install IBM Cloud CLI
RUN curl -L https://download.clis.test.cloud.ibm.com/ibm-cloud-cli/2.35.0/IBM_Cloud_CLI_2.35.0_amd64.tar.gz -o /tmp/ibmcloud.tar.gz && \
    tar -xzf /tmp/ibmcloud.tar.gz -C /tmp && \
    mv /tmp/Bluemix_CLI/bin/ibmcloud /usr/local/bin/ && \
    rm -rf /tmp/ibmcloud.tar.gz /tmp/Bluemix_CLI && \
    chmod +x /usr/local/bin/ibmcloud

COPY --from=uv --chown=app:app /app/.venv /app/.venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --chown=app:app . /app/

# Place executables in the environment at the front of the path
ENV PATH="/usr/local/bin:/app/.venv/bin:$PATH"

EXPOSE 8000

WORKDIR /app
USER app
CMD ["sh","-c","ibmcloud login --apikey $IBMCLOUD_API_KEY -r $IBMCLOUD_REGION && uv run -m ibmcloud_base_agent.main --config agent.yaml"]
