# Architecture

## Request flow

```text
CLI
 ├─ PM Agent        → PRD
 ├─ Architect Agent → implementation plan
 └─ Developer Agent → model/tool loop → project workspace
```

PM and Architect return text artifacts. The Developer receives those artifacts plus repository instructions, then iterates between a provider response and local tool results until it returns a final answer or reaches the configured turn limit.

## Provider boundary

`minicode.providers` adapts two native tool-call formats to a small shared `AgentTurn` type:

- OpenAI Responses API (`function_call` and `function_call_output` items).
- OpenAI-compatible Chat Completions (`tool_calls` and `tool` messages).
- Anthropic Messages API (`tool_use` and `tool_result` blocks).

Provider history remains provider-native so each adapter can replay the correct conversation format. OpenAI Responses requests set `store=False`; MiniCode keeps the local session history needed to continue the tool loop.

## Workspace boundary

The file tools resolve project paths and reject paths that escape the selected workspace, local environment files, private-key files, and runtime configuration directories. Directory searches skip common generated and dependency folders. Writes, precise edits, and each shell command call the approval prompt by default.

Approval is a user prompt, not process isolation. Commands run as the current operating-system user. Use an external container or disposable worktree when stronger isolation is needed.

## Session and artifacts

- Full resumable conversation state: `~/.minicode/sessions/<id>.json`.
- PRD, architecture, and original request: `~/.minicode/runs/<id>/`.
- Generated and modified source: the selected project workspace.
- `minicode forget <id>` removes the local session and its planning artifacts.

Session files use owner-only file permissions where the platform supports them. They may include source excerpts and user prompts; protect or delete them according to the sensitivity of the project.
