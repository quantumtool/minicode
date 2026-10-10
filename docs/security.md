# Security boundaries

MiniCode runs models and local tools in separate parts of the process:

- The model provider receives user prompts, the PM and Architect outputs, root `AGENTS.md`/`CLAUDE.md` instructions, loaded skills, and the file or command output the agent requests.
- The local tool handler checks workspace paths, blocks common environment files, private-key files, and credential directories, and asks before file writes, edits, and commands.
- Shell subprocesses omit environment variables whose names look like API keys, access keys, secrets, tokens, passwords, credentials, auth values, or cookies.
- The selected provider key is read from the current process environment and is not intentionally added to model prompts or session JSON.

## What the protections do not provide

- Path checks apply to MiniCode file tools; they do not sandbox shell processes.
- An approved shell command can access resources available to the current operating-system account, including network access and environment variables.
- Environment-variable filtering is name-based and cannot detect secrets under arbitrary names or credentials stored in local files.
- `--yes` approves every file write, edit, and shell command for that run.
- Content from repository instructions, skills, files, and tool output can be malicious or misleading. Review requested actions and generated diffs.
- Session JSON can contain prompts, source snippets, and command output. It is stored under the current user's home directory, not encrypted by MiniCode.

For untrusted repositories, run MiniCode inside a disposable container or virtual machine, use narrowly scoped credentials, and do not use `--yes` on a host with valuable data.

Review the data handling terms of the selected model provider before sending private source code. File and command output is included in API requests when the Developer Agent asks for it.

## Credentials in Git history

The earlier public repository contains a tracked `.env` file and at least one value matching a credential-like pattern. This refresh removes `.env` from the current project tree and ignores future local secret files. That does not remove old public commits. Rotate any real credential that may have appeared there. Before replacing a public branch, decide whether to rewrite history and coordinate that change with collaborators; rewriting history changes commit IDs and can disrupt existing clones.

Never put a real key in `.env.example`, an issue, a pull request, a log, or a source file.
