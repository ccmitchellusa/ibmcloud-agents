# Repository Guidelines

## Project Structure & Module Organization
- `src/` contains:
  - `agents/`: YAML definitions for specialized agents.
  - `common/`: Core logic and base classes (`ibm_cloud_base.py`, `agent_factory.py`).
  - `supervisor_agent/` & `kingsmen_agent/`: Logic for coordination agents.
- `tests/` holds pytest suites (`integration/test_agent_startup.py`, fixtures) that verify agent bootstrapping and service wiring.
- `docs/` aggregates tutorials, reference material, and generated outputs; keep sizeable assets there.
- Root scripts (`run.sh`, `run_web.sh`, `start.sh`) start local stacks, while `agent.yaml` and the `ibmcloud_mcp_*_config.json` files define deployable agent profiles.

## Build, Test, and Development Commands
- `uv sync --reinstall` installs pinned Python 3.12 dependencies from `pyproject.toml` and `uv.lock`.
- `make run` (or `./run.sh`) launches the MCP-enabled agent server with the default Supervisor agent.
- `make dev` provides a hot-reload development server; use it when iterating on handlers.
- `make test`, `make pytest-examples`, and `make test-curl` cover unit, documentation, and endpoint smoke tests respectively; run them before opening a PR.

## Coding Style & Naming Conventions
- Format Python with `black` (line length 200) and manage imports with `isort`; `make lint` chains these with `ruff`, `flake8`, and security/static analyzers.
- Keep functions and modules `snake_case`, classes `PascalCase`, and constants `UPPER_SNAKE_CASE`. When adding new agents, add a new YAML file to `src/agents/`.
- Type hints are required (`mypy --strict` in the toolchain); favor explicit return types and dataclasses for structured payloads.

## Testing Guidelines
- Place new tests beside the code they exercise under `tests/`; name files `test_<feature>.py` and fixtures under `tests/fixtures/`.
- Prefer async-compatible tests (pytest asyncio auto-mode). Use `pytest.mark.asyncio` when a coroutine is under test.
- Use `make coverage` to produce Markdown and HTML reports; maintain or raise coverage for touched modules, especially orchestration paths in `src/supervisor_agent`.

## Commit & Pull Request Guidelines
- Write imperative, descriptive commit subjects (e.g., “Add dynamic team management for supervisor agent”) and keep summaries under 72 characters.
- Reference related issues in the commit body or PR description and describe the agent scenarios you validated (commands run, sample requests).
- For PRs, list required environment variables, attach relevant `docs/` screenshots or `curl` transcripts, and confirm `make test` and `make lint` pass locally.

## Configuration & Secrets
- Copy `.env.example` to `.env` and populate provider API keys; never commit secrets or service credentials.
- Keep shared agent settings in the provided `ibmcloud_mcp_*_config.json` files; document any new keys in `docs/` so operators can mirror production configs.
