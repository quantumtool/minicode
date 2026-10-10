# Security policy

Do not report a vulnerability in a public issue if it includes a credential or exploitable details. Contact the repository maintainers privately and include reproduction steps without live secrets.

If a credential was committed, revoke or rotate it with its provider first. Removing the file from the latest commit does not remove it from Git history. History rewriting may be necessary before republishing, and collaborators will need to reconcile their clones.

MiniCode is a local prototype. Its approval prompts are not an operating-system sandbox. Treat `--yes` and shell access as full trust in the current account and workspace.
