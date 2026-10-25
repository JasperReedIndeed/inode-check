# inode-check

**Database is locked, or state showing up under the wrong agent?** Two folders that look separate can be one file on disk — a hardlink, a symlink alias, or one path nested inside the other. This is a small, read-only check for exactly that question.

A small, AI-assisted Python utility comparing two existing paths by filesystem metadata. Free source; MIT licensed. It never opens config, credential, database or conversation contents.

## What the check establishes

On a typical local POSIX filesystem, two paths with the same `(st_dev, st_ino)` refer to the same filesystem object. Hardlinks or symlink aliases can make different-looking paths lead to the same file. The tool also checks resolved directory nesting.

Ordinary copies and copy-on-write clones generally have distinct file identities, even when they contain identical bytes or share storage blocks. Nesting is not the same as shared database identity. Mounts, containers and network filesystems may have different semantics; this is a small same-machine check, not a universal identity proof or security audit. No mount-specific behavior was tested.

The examples and tests are synthetic demonstrations. We have not observed a real OpenClaw incident or customer failure using this tool. It does not detect equal copied credentials, configured policies or actual isolation. A live filesystem can change while being checked.

## Run

Requires Python; executed locally on macOS with Python 3.12. Other platforms and versions have not been independently tested.

```bash
python3 -B inode-check.py /absolute/path/to/first /absolute/path/to/second
```

Replace the example paths with existing files or folders you own or are authorized to inspect. No automatic home/profile discovery, network request, content read or file modification is performed by the diagnostic.

- Exit 0: different observed file identities, no resolved nesting. NOT a security pass.
- Exit 1: same observed file identity OR resolved nesting. Read the message to distinguish them.
- Exit 2: could not check. Missing/inaccessible inputs are not clean results.

**Output privacy:** this FREE checker prints the supplied paths and file identities. Review and redact output before posting it. Do not provide paths containing sensitive identifiers if they might enter logs or shell history.

## Tests

```bash
python3 -B -m unittest discover -s tests -v
```

Tests create real temporary filesystem fixtures: distinct items, hardlinks, nesting, symlink alias, missing paths and metadata access to a mode-000 file. The mode-000 case demonstrates metadata access, not a rigorous proof that arbitrary content reads are impossible; privileged users can bypass ordinary permission bits. Tests are not an installed OpenClaw integration test.

## When this is the check you need

If two agents were meant to be separate deployments and one symptom shows up — `database is locked`, memories or sessions appearing under the wrong agent, or an agent that fails to start while another runs — the first question is whether their folders are actually separate objects on disk. That is all this script answers, and it answers it without reading anything.

A plain page explaining the check and its limits: https://jasperreedindeed.github.io/inode-check/

## Related paid tool

[Agent Deployment Footprint Comparator](https://omnihustleautomation.gumroad.com/l/bmyzpq) is a separate $29 product from this project's seller. It compares multiple explicitly selected same-machine default-layout candidates and prepares a path-redacted JSON report. It also includes an optional declaration-only mode. This free checker is usable on its own; no purchase is required. No measured customer time savings or demand is claimed.

For a broader single-gateway audit, start with OpenClaw's own free commands. Its docs describe agent-directory scope and explain why default working directories are not security boundaries:
https://docs.openclaw.ai/concepts/multi-agent

## License

The repository code is MIT licensed. That does not grant redistribution rights to the separate paid product. AI assistance is disclosed; no upstream endorsement or real incident is implied.
