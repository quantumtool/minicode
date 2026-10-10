# GitHub upload checklist

The refreshed source tree is on the local branch `codex/modernize-agent-runtime`. No remote branch has been pushed or changed.

Before publishing:

1. Review the branch diff and the intended repository owner, project group, and visibility.
2. Rotate any real key that may have appeared in the old public `.env` history. The refresh removes `.env` from the current tree, but old commits on the existing remote still contain their original contents.
3. Decide whether to keep the existing history or coordinate a history rewrite. Rewriting a public default branch changes commit IDs and affects every existing clone; a normal new commit does not erase old secret-bearing commits.
4. Choose a repository license if the project will be public. No license has been added because the project owner must choose the terms.
5. Set provider credentials only in a local `.env`, `~/.minicode/.env`, or an environment variable; never add them to this branch.
6. Install from a clean clone and run an example against a disposable workspace before sharing the branch with the team.
