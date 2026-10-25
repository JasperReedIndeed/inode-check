#!/usr/bin/env python3
"""inode-check: are these two paths the same file, or is one inside the other?

The whole trick behind a "separate" deployment that shares state:

    os.stat(path).st_dev, os.stat(path).st_ino

Two different paths can report the same device+inode pair, for example through
a hard link or a symlink alias. Ordinary copies and copy-on-write clones generally
have distinct file identities. Mount and network filesystem behavior is untested.

Read-only metadata inspection: stat and realpath, never file contents.
The free checker prints paths and file identities; redact output before sharing.

Usage:
    python3 inode-check.py /srv/alpha /srv/beta
    python3 inode-check.py /srv/alpha/agents/main/agent/openclaw-agent.sqlite \
                           /srv/beta/agents/main/agent/openclaw-agent.sqlite

Exit codes: 0 = distinct, 1 = same file or nested, 2 = could not check.
"""
import os
import sys


def identity(path):
    st = os.stat(path)
    return st.st_dev, st.st_ino


def inside(child, parent):
    child = os.path.realpath(child)
    parent = os.path.realpath(parent)
    return child == parent or child.startswith(parent.rstrip(os.sep) + os.sep)


def main(argv):
    if len(argv) != 2:
        print("usage: inode-check.py PATH_A PATH_B", file=sys.stderr)
        return 2
    a, b = argv
    try:
        ida, idb = identity(a), identity(b)
        nested = inside(a, b) or inside(b, a)
    except (OSError,ValueError,RuntimeError):
        print('cannot stat or resolve: check paths, access and symlink targets', file=sys.stderr)
        return 2

    if ida == idb:
        print(f"SAME FILE  dev={ida[0]} ino={ida[1]}")
        print(f"  {a}\n  {b}")
        return 1
    if nested:
        print("NESTED     one path resolves inside the other")
        print(f"  {a}\n  {b}")
        return 1
    print(f"distinct   dev/ino {ida} vs {idb}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
