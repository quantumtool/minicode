# Publish MiniCode source and downloads

This project publishes source code to the GitHub repository and installable files as assets on a GitHub Release. The current package version is `0.2.0`.

## Publish the source code

The refresh is on branch `codex/modernize-agent-runtime`, based on the existing `main` history. Push it and open a pull request so the update can be reviewed and merged into `main`:

```bash
git push -u origin codex/modernize-agent-runtime
```

On GitHub, choose **Compare & pull request**, set the base to `main`, review the changes, and merge the pull request. This keeps the existing repository history; it does not remove files from old commits.

## Build downloadable files

Use Python 3.11 or newer. From the repository root:

```bash
python -m pip install build
python -m build
```

This creates a wheel for `pip` installation and a source distribution in `dist/`. The release bundle also includes a full source ZIP and `SHA256SUMS.txt`.

## Publish the GitHub Release

Tag the reviewed source commit and push the tag:

```bash
git tag -a v0.2.0 -m "MiniCode 0.2.0" <reviewed-commit>
git push origin v0.2.0
```

On GitHub, open **Releases → Draft a new release**, select tag `v0.2.0`, and attach these files from `dist/`:

- `minicode_agent-0.2.0-py3-none-any.whl` — install with `python -m pip install <downloaded-wheel>`.
- `minicode_agent-0.2.0.tar.gz` — source distribution for Python packaging tools.
- `minicode-source-0.2.0.zip` — complete project source and documentation.
- `SHA256SUMS.txt` — checksums for the three files above.

Publish the release to make the download links in both READMEs available. GitHub also creates its own source ZIP and tarball for the release tag.

## Before publishing publicly

- Rotate any real credential that appeared in the old public `.env` history. Removing `.env` from the current tree does not remove it from old commits.
- No project license is included. Choose and add a license before inviting others to reuse or redistribute the source.
- Keep provider API keys in a local `.env` or environment variables; never upload them.
