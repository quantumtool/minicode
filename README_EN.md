# MiniCode

MiniCode is a local multi-agent coding assistant. It keeps a PM → Architect → Developer workflow and gives the Developer an iterative tool loop for inspecting and changing a real project workspace.

The design takes inspiration from public Codex and Claude Code workflows—project instructions, tool use, workspace controls, approvals, and resumable sessions. MiniCode is an independent project, not an official implementation of either product.

## Features

- Sequential PM, Architect, and Developer roles.
- OpenAI Responses API, Anthropic Messages API, and OpenAI-compatible Chat Completions.
- Loads root `AGENTS.md`, root `CLAUDE.md`, and `.minicode/skills/*/SKILL.md`.
- Tools for listing, reading, searching, writing, editing, and running commands in a workspace.
- Prompts before each write, edit, and shell command unless `--yes` is explicitly used.
- Saves resumable sessions under `~/.minicode/sessions/` and planning artifacts under `~/.minicode/runs/`.

## Install

Requires Python 3.11+ and an API account for the selected provider.

```bash
git clone https://github.com/quantumtool/minicode.git
cd minicode
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `MINICODE_PROVIDER` to `openai` or `anthropic`, set `MINICODE_MODEL` to a model available to your account, then provide `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in a local `.env` file. MiniCode reads `.env` from the current directory, `~/.minicode/.env`, or the source checkout root; `MINICODE_ENV_FILE` selects a specific file. Existing process environment variables take precedence. OpenAI uses Responses by default. Set `MINICODE_OPENAI_API=chat_completions` and `OPENAI_BASE_URL` for compatible endpoints that do not support Responses.

## Run

```bash
minicode run "Add password reset to the login page" --workspace .
minicode plan "Build a todo web app" --workspace .
minicode sessions
minicode resume <session-id> "Add mobile layout"
minicode forget <session-id>
```

The generated code is written to the selected workspace. PRD and architecture notes are saved under `~/.minicode/runs/<session-id>/`.

Writes and shell commands require approval by default. `--yes` disables those prompts; it is not an OS sandbox, so use it only in a disposable isolated workspace.

## Scope and security

MiniCode does not currently provide the Codex sandbox or hosted harness, nor full Claude Code permissions, hooks, MCP, plugins, browser/computer tools, or native CLI login. See [the current capability comparison](docs/modernization.md) and [security notes](docs/security.md).

See the [GitHub upload checklist](docs/github-upload.md) before publishing this refresh.

Do not commit API keys. The earlier public repository history included a `.env` file. Deleting it from the current tree does not remove it from old commits; rotate any real key that may have been present and review history cleanup before republishing. See [SECURITY.md](SECURITY.md).
