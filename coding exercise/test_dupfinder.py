#!/usr/bin/env python3
"""Test harness for dupfinder.py.

Usage:
    python3 test_dupfinder.py          # run every scope
    python3 test_dupfinder.py 2        # run scope 2 only

Each case builds a fresh FakeFS, calls your find_dups(root, fs), and checks
the result against the ground truth by file identity — so any path that
reaches a file is accepted, but a file listed twice, a missing group, or an
extra group fails the case.
"""
import contextlib
import io
import sys
import time
import traceback

from fakefs import FakeFS
from dupfinder import find_dups

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

MB = 1024 * 1024


# ---------------- builders: each returns (fs, root) ----------------
def plain_tree():
    fs = FakeFS()
    fs.add_file("/docs/a.txt", b"hello")
    fs.add_file("/docs/b.txt", b"world")
    fs.add_file("/docs/sub/c.txt", b"hello")
    fs.add_file("/img/x.png", b"\x89PNG-1")
    fs.add_file("/img/y.png", b"\x89PNG-1")
    fs.add_file("/img/z.png", b"\x89PNG-2")
    fs.add_dir("/empty")
    fs.add_file("/notes/d.txt", b"hello")
    return fs, "/"


def no_dups():
    fs = FakeFS()
    for i in range(6):
        fs.add_file(f"/f{i}", str(i).encode())
    return fs, "/"


def empty_root():
    return FakeFS(), "/"


def root_is_a_subdir():
    fs, _ = plain_tree()
    return fs, "/docs"            # only a.txt and sub/c.txt are inside


def symlink_cycle():
    fs = FakeFS()
    fs.add_file("/a/f1", b"x")
    fs.add_file("/a/b/f2", b"x")
    fs.add_symlink("/a/b/loop", "/a")       # /a/b/loop/b/loop/b/... forever
    fs.add_symlink("/a/b/self", "/a/b")
    return fs, "/"


def symlink_to_sibling():
    fs = FakeFS()
    fs.add_file("/p/r/f", b"k")
    fs.add_file("/p/q/g", b"k")
    fs.add_symlink("/p/q/s", "/p/r")        # /p/r/f is also reachable as /p/q/s/f
    return fs, "/"


def unreadable_file():
    fs = FakeFS()
    fs.add_file("/d/ok1", b"m")
    fs.add_file("/d/ok2", b"m")
    fs.add_file("/d/secret", b"m")
    fs.deny("/d/secret")
    return fs, "/"


def unreadable_dir():
    fs = FakeFS()
    fs.add_file("/d2/open/f1", b"n")
    fs.add_file("/d2/locked/f2", b"n")
    fs.add_file("/d2/f3", b"n")
    fs.deny("/d2/locked")
    return fs, "/"


def deep_chain():
    fs = FakeFS()
    fs.add_file("/deep/" + "/".join(f"d{i}" for i in range(2000)) + "/leaf", b"z")
    fs.add_file("/deep/leaf2", b"z")
    return fs, "/"


def wide_dir():
    fs = FakeFS()
    for i in range(5000):
        fs.add_file(f"/wide/f{i:04d}", str(i % 7).encode())
    return fs, "/"


def everything_at_once():
    fs = FakeFS()
    fs.add_file("/a/f1", b"x")
    fs.add_file("/a/b/f2", b"x")
    fs.add_symlink("/a/b/loop", "/a")
    fs.add_file("/d/ok", b"x")
    fs.add_file("/d/secret", b"x")
    fs.deny("/d/secret")
    fs.add_file("/locked/f", b"x")
    fs.deny("/locked")
    fs.add_file("/deep/" + "/".join(f"d{i}" for i in range(1500)) + "/leaf", b"x")
    return fs, "/"


def big_pairs():
    fs = FakeFS()
    fs.add_file("/big/a.bin", big=(1, 6 * MB))
    fs.add_file("/big/b.bin", big=(1, 6 * MB))      # same seed + size -> identical
    fs.add_file("/big/c.bin", big=(2, 6 * MB))      # same size, different content
    fs.add_file("/big/d.bin", big=(3, 9 * MB))      # unique size: no need to read it at all
    fs.add_file("/big/s1.txt", b"q")
    fs.add_file("/big/s2.txt", b"q")
    return fs, "/"


def big_all_unique_sizes():
    fs = FakeFS()
    for i in range(20):
        fs.add_file(f"/u/f{i}.bin", big=(i, 5 * MB + i))   # 20 distinct sizes -> nothing to hash
    return fs, "/"


def big_and_unreadable():
    fs = FakeFS()
    fs.add_file("/m/a.bin", big=(7, 5 * MB))
    fs.add_file("/m/b.bin", big=(7, 5 * MB))
    fs.add_file("/m/c.bin", big=(7, 5 * MB))
    fs.deny("/m/c.bin")                             # same twin, but unreadable -> not in the group
    return fs, "/"


SCOPES = {
    1: ("a plain tree: walk, group by content, keep groups of 2+", [
        ("three groups' worth of files, one empty dir", plain_tree),
        ("no duplicates -> []", no_dups),
        ("empty root -> []", empty_root),
        ("root is a subdirectory: only files under it count", root_is_a_subdir),
    ]),
    2: ("hazards: cycles, permissions, depth, width", [
        ("symlink cycle: /a/b/loop -> /a (visited by identity, not by path)", symlink_cycle),
        ("symlink to a sibling dir: the same file reachable by two paths, list it once", symlink_to_sibling),
        ("unreadable file: skip it, keep the rest", unreadable_file),
        ("unreadable directory: skip its subtree, keep the rest", unreadable_dir),
        ("directory nested 2,000 deep (recursion dies here)", deep_chain),
        ("one directory with 5,000 files", wide_dir),
        ("all of the above in one tree", everything_at_once),
    ]),
    3: ("files too big to load: size first, chunked hash only on size twins", [
        ("6 MB twins + a same-size impostor + a 9 MB loner + two tiny twins", big_pairs),
        ("20 big files with 20 distinct sizes -> nothing should be read (watch the time)", big_all_unique_sizes),
        ("big twins where one copy is unreadable", big_and_unreadable),
    ]),
}


def check(fs, root, got):
    truth = fs._truth(root)                           # inode -> (key, path)
    by_key = {}
    for ino, (key, path) in truth.items():
        by_key.setdefault(key, set()).add(ino)
    expected = {frozenset(s) for s in by_key.values() if len(s) >= 2}
    if not isinstance(got, list):
        return f"returned {type(got).__name__}, expected list of lists"
    seen, result = set(), set()
    for g in got:
        if not isinstance(g, (list, tuple)):
            return f"group is {type(g).__name__}, expected a list of paths"
        ids = set()
        for p in g:
            try:
                ino = fs.identity(p)[1]
            except Exception:
                return f"path does not exist: {p!r}"
            if ino in seen:
                return f"the same file appears twice: {p!r}"
            seen.add(ino)
            ids.add(ino)
        result.add(frozenset(ids))
    if result == expected:
        return None
    path_of = {ino: path for ino, (key, path) in truth.items()}
    missing = [g for g in expected if g not in result]
    extra = [g for g in result if g not in expected]
    msg = f"expected {len(expected)} group(s), got {len(result)}"
    if missing:
        ex = sorted(path_of[i] for i in next(iter(missing)))
        msg += f"\n      a missing group: {ex[:4]}{' ...' if len(ex) > 4 else ''}"
    if extra:
        ex = sorted(path_of.get(i, '?') for i in next(iter(extra)))
        msg += f"\n      an extra/wrong group: {ex[:4]}{' ...' if len(ex) > 4 else ''}"
    return msg


def show_prints(text, limit=15):
    if not text:
        return
    lines = text.rstrip("\n").split("\n")
    print(f"      {YELLOW}your prints:{RESET}")
    for ln in lines[:limit]:
        print(f"      │ {ln}")
    if len(lines) > limit:
        print(f"      │ ... ({len(lines) - limit} more lines)")


def show_exception(exc):
    frames = traceback.extract_tb(exc.__traceback__)
    mine = [f for f in frames if f.filename.endswith("dupfinder.py") and not f.filename.endswith("test_dupfinder.py")]
    where = f" at dupfinder.py:{mine[-1].lineno} in {mine[-1].name}()" if mine else ""
    if isinstance(exc, NotImplementedError):
        print(f"      {YELLOW}not implemented yet{RESET}")
    else:
        print(f"      {RED}{type(exc).__name__}: {str(exc)[:90]}{where}{RESET}")


def run_scope(n):
    title, cases = SCOPES[n]
    print(f"\n{BLUE}{BOLD}Scope {n} · {title}{RESET}")
    passed = 0
    for name, build in cases:
        fs, root = build()
        buf = io.StringIO()
        t0 = time.perf_counter()
        try:
            with contextlib.redirect_stdout(buf):
                got = find_dups(root, fs)
        except BaseException as exc:
            if isinstance(exc, KeyboardInterrupt):
                raise
            print(f"  {RED}✗{RESET} {name}")
            show_prints(buf.getvalue())
            show_exception(exc)
            continue
        elapsed = time.perf_counter() - t0
        timing = f"  {YELLOW}({elapsed:.2f} s){RESET}" if elapsed > 0.05 else ""
        problem = check(fs, root, got)
        if problem is None:
            print(f"  {GREEN}✓{RESET} {name}{timing}")
            show_prints(buf.getvalue())
            passed += 1
        else:
            print(f"  {RED}✗{RESET} {name}{timing}")
            show_prints(buf.getvalue())
            print(f"      {problem}")
    color = GREEN if passed == len(cases) else RED
    print(f"  {color}{passed}/{len(cases)} passed{RESET}")
    return passed, len(cases)


def main():
    wanted = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(SCOPES)
    total_pass = total = 0
    for n in wanted:
        p, t = run_scope(n)
        total_pass += p
        total += t
    color = GREEN if total_pass == total else RED
    print(f"\n{color}{BOLD}TOTAL {total_pass}/{total}{RESET}\n")


if __name__ == "__main__":
    main()
