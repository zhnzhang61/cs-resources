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
    # three layers, one per scope: walk the disk -> cheap grouping by size -> exact grouping by hash
    files = walk(root, fs)                                  # every readable file, each real file once
    result = []
    for same_size in group_by_size(files, fs):              # only size twins get read at all
        result.extend(group_by_hash(same_size, fs))
    return result


def walk(root, fs):
    # BFS with an explicit queue (no recursion: 2,000-deep dirs). visited is keyed by fs.identity,
    # not by path, because a symlink makes the same directory appear under a second path -> cycle.
    files = []
    seen_dirs = set()
    seen_files = set()
    queue = deque([root])
    while queue:
        d = queue.popleft()
        try:
            ident = fs.identity(d)
            if ident in seen_dirs:
                continue
            seen_dirs.add(ident)
            children = fs.list_dir(d)
        except OSError:                                     # PermissionError is an OSError: skip this dir, keep going
            continue
        for p in children:
            if fs.is_dir(p):
                queue.append(p)
                continue
            try:
                ident = fs.identity(p)
            except OSError:                                 # dangling symlink etc.
                continue
            if ident not in seen_files:                     # the same file reachable by two paths: list it once
                seen_files.add(ident)
                files.append(p)
    return files


def group_by_size(files, fs):
    # size is free (metadata); two files of different size cannot be equal, so most files never get read
    by_size = {}
    for p in files:
        try:
            by_size.setdefault(fs.size(p), []).append(p)
        except OSError:
            continue
    return [g for g in by_size.values() if len(g) >= 2]


def group_by_hash(paths, fs):
    # exact check: hash the content in chunks (files may be too big to load), group by digest
    by_hash = {}
    for p in paths:
        h = hashlib.sha256()
        try:
            for chunk in fs.read_chunks(p):
                h.update(chunk)
        except OSError:                                     # unreadable file: it cannot be in any group
            continue
        by_hash.setdefault(h.digest(), []).append(p)
    return [g for g in by_hash.values() if len(g) >= 2]


if __name__ == "__main__":
    from fakefs import FakeFS
    MB = 1024 * 1024
    groups = lambda out: sorted(sorted(g) for g in out)      # groups and paths come back in any order

    fs = FakeFS()
    fs.add_file("/docs/a.txt", b"hello"); fs.add_file("/docs/sub/c.txt", b"hello")
    fs.add_file("/img/x.png", b"\x89PNG"); fs.add_file("/img/y.png", b"\x89PNG"); fs.add_file("/img/z.png", b"other")
    fs.add_dir("/empty")
    assert groups(find_dups("/", fs)) == [["/docs/a.txt", "/docs/sub/c.txt"], ["/img/x.png", "/img/y.png"]]
    assert find_dups("/empty", fs) == []                                   # root with nothing in it
    fs.add_symlink("/docs/sub/loop", "/docs")                              # a cycle: must terminate, each file once
    assert groups(find_dups("/docs", fs)) == [["/docs/a.txt", "/docs/sub/c.txt"]]
    fs.deny("/img/y.png")                                                  # unreadable: skipped, x.png loses its twin
    assert find_dups("/img", fs) == []
    fs.add_file("/big/a.bin", big=(1, 6 * MB)); fs.add_file("/big/b.bin", big=(1, 6 * MB)); fs.add_file("/big/c.bin", big=(2, 9 * MB))
    assert groups(find_dups("/big", fs)) == [["/big/a.bin", "/big/b.bin"]]   # too big to load: size first, then chunked hash
    print("inline tests: all 5 pass   (python3 test_dupfinder.py runs the 14-case harness)")
