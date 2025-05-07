# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1 
ENV UV_LINK_MODE=copy 
#ENV UV_PROJECT_ENVIRONMENT=/app

COPY uv.lock pyproject.toml /app/

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable   

FROM python:3.13-slim-bookworm

COPY --from=uv --chown=app:app /app/.venv /app/.venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# Copy IBM Cloud CLI linux-amd64 binary (the MCP Server) into the path.
COPY ./dist/ibmcloud /usr/local/bin/ibmcloud
COPY . /app/


# Place executables in the environment at the front of the path
ENV PATH="/usr/local/bin:/app/.venv/bin:$PATH"

EXPOSE 8000

WORKDIR /app
CMD ["sh","-c","/usr/local/bin/ibmcloud","login","--apikey","$IBMCLOUD_API_KEY","&&","/usr/local/bin/uv","run","-m","pirate_agent_a2a.main","--config","agent.yaml"]
