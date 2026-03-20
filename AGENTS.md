# Repository Guidelines

## Project Structure & Module Organization
- `servers/`: stateless MCP servers (`math`, `unit`, `osint`, `time`, `lang`, `crypto`, `graphs`, `chem`). Most expose tools from `app.py`; `unit/` also splits logic into `tools/` and `utils/`.
- `software/`: stateful Light apps (`LightSystem`, `LightTalk`, `LightShop`, `LightWeather`, `LightFlight`, `LightStock`, `LightNews`) plus shared helpers in `software/utils/`.
- `client/`: agent runtime, tool-calling backend, token accounting, and RAG integration.
- `benchmark/`: evaluation logic (`judge.py`), generated instructions, and dataset (`benchmark/data/data.parquet`).
- `config/`: server registration presets (`general.yaml`, `light.yaml`).

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create and activate local environment.
- `pip install -r requirements.txt`: install pinned dependencies.
- `./start_servers.sh`: launch MCP servers on ports `8000-8007`.
- `./start_softwares.sh`: launch Light apps on ports `9000-9006`.
- `python check-server.py`: quick connectivity/tool-call sanity check.
- `python run_benchmark.py -m gpt-4o -t config/general.yaml --method list_all`: run benchmark evaluation.
- `python run_benchmark.py -m gpt-4o -t config/light.yaml -g`: generate benchmark instructions.

## Coding Style & Naming Conventions
- Python code uses 4-space indentation, type hints, and `snake_case` for functions/variables; use `PascalCase` for classes.
- Keep each MCP tool focused and return structured status payloads (`{"status": "ok|failed|error", ...}`).
- Follow existing module pattern: FastMCP entrypoint in `app.py`, session/state logic in `session.py` or helper modules.

## Testing Guidelines
- No dedicated `tests/` suite is currently committed. Validate changes with targeted runtime checks:
  - start affected server/app,
  - execute representative tool calls,
  - run `run_benchmark.py` for regression-sensitive changes.
- If adding tests, place them under a new `tests/` package and use `test_<module>.py` naming.

## Commit & Pull Request Guidelines
- Current history favors short, imperative summaries (for example, `Added token computations.` / `Fixed some bugs.`).
- Keep commit messages concise and scoped to one change.
- PRs should include: purpose, impacted modules (for example `servers/unit/tools/`), config/data changes, reproduction commands, and sample outputs for behavior changes.
