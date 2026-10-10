# Modernization reference: Codex and Claude Code

**Reference checked: 2026-10-11.** Product behavior changes over time; verify the linked official documentation before treating a capability or model name as current.

## What the current products provide

- The Codex CLI and related agent documentation describe local coding workflows with repository instructions, tool calls, approval settings, and sandbox controls. The OpenAI agent platform also offers managed Codex harness sessions, environments, function tools, MCP, recovery, and multi-agent capabilities.
- Claude Code documents an iterative tool-use workflow, repository and user settings, permission rules, session continuation, hooks, skills, plugins, and MCP integrations.
- Both providers expose tool-use APIs, but the wire formats and state models differ. MiniCode keeps separate provider adapters rather than assuming the same schema works everywhere.

## MiniCode 0.2 comparison

| Area | MiniCode 0.2 | Scope limit |
| --- | --- | --- |
| Agent roles | Sequential PM → Architect → Developer | No parallel or delegated subagents |
| Coding loop | Local repeated model/tool calls | No official Codex or Claude Code harness |
| Workspace tools | List, read, search, write, edit, shell | No OS-level sandbox; shell runs as the current user |
| Permissions | Per-operation prompt for writes and shell | No product-grade allow/deny rule language |
| Context | Root `AGENTS.md`, root `CLAUDE.md`, simple local `SKILL.md` loading | No full Codex/Claude settings or skill lifecycle |
| Sessions | Local JSON history and resume command | No cloud sync, compaction, branch/worktree management, or long-running task service |
| Providers | OpenAI Responses, compatible Chat Completions, Anthropic Messages | API keys only; no Codex/Claude CLI login or subscription billing integration |
| Integrations | None beyond the built-in local tools | MCP, plugins, hooks, web, browser, and computer-use tools are not implemented |

The refresh moves MiniCode from a one-shot code-document generator to a local tool-using coding agent while preserving the original role pipeline. It deliberately does not claim feature parity with either mature product.

## Official references

- [Codex CLI](https://learn.chatgpt.com/docs/codex/cli)
- [OpenAI agents and runtime choices](https://developers.openai.com/api/docs/guides/agents)
- [OpenAI Agents API overview](https://developers.openai.com/api/docs/guides/agents-api/overview)
- [OpenAI Responses API function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Claude Code overview](https://code.claude.com/docs/en/overview)
- [Claude Code permissions](https://code.claude.com/docs/en/permissions)
- [Claude Code project memory](https://code.claude.com/docs/en/memory)
- [Claude Messages API tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
