# Contributing

1. Create a virtual environment and install the project with `python -m pip install -e .`.
2. Read the current architecture and security notes before changing provider or workspace behavior.
3. Keep provider-specific API payloads inside `minicode/providers/`; avoid sharing one provider's history format with another.
4. Keep filesystem and command permissions explicit. Do not introduce an automatic approval default.
5. Do not commit `.env`, tokens, generated project output, session transcripts, or personal editor settings.
6. Describe behavior changes, configuration changes, and any manual verification in your pull request.

When adding support for a vendor API or coding-agent feature, link to its current official documentation and state which parts MiniCode implements versus delegates.
