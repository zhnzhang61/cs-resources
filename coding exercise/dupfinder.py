#!/usr/bin/env python3
"""
Duplicate File Finder — on a (fake) real filesystem

find_dups(root, fs) -> list[list[str]]

You are NOT given the LeetCode string format. You are given a root path and
an `fs` object (see fakefs.py) with:

    fs.list_dir(path) -> list[str]       fs.is_dir(path) -> bool
    fs.size(path) -> int                 fs.read_file(path) -> bytes
    fs.read_chunks(path, chunk_size) -> iterator of bytes
    fs.identity(path) -> (dev, inode)

Return every group of files with identical content, groups of size >= 2.
Any path that reaches the file is accepted, but each file must appear once.
Order of groups and of paths inside a group does not matter.

Scope 1  a plain tree: walk it, group by content, keep groups >= 2.

Scope 2  the walk meets real-world hazards and must not crash or loop:
         symlinks that create cycles (same directory reached twice — key your
         visited set by fs.identity, not by path), unreadable files and
         directories (PermissionError: skip them, keep going), a directory
         nested 2,000 deep (recursion dies — iterate), a directory with 5,000
         entries.

Scope 3  files too big to load: fs.read_file raises MemoryError above 4 MB.
         Group by fs.size first (free), hash with fs.read_chunks only inside
         same-size groups, never read a file that has no size twin.

Run the tests:  python3 test_dupfinder.py        (all scopes)
                python3 test_dupfinder.py 2      (scope 2 only)
or just run this file (F5 in VS Code).
"""
import hashlib
from collections import deque


def find_dups(root: str, fs) -> list[list[str]]:
    raise NotImplementedError


if __name__ == "__main__":
    from test_dupfinder import main
    main()
