#!/usr/bin/env python3
"""
Duplicate File Finder — LeetCode 609, then a five-question interview on a (fake) real disk

THE SETTING
    You get a root path and an `fs` object (fakefs.py). The reported interface is two calls:

        fs.list_dir(path) -> list[str]    full paths of ONE directory's entries (it does not descend)
        fs.is_dir(path)   -> bool

    The follow-ups add four more (the real-disk call in brackets):

        fs.size(path)        -> int              [os.path.getsize]
        fs.read_file(path)   -> bytes            [open(p, "rb").read()]   raises MemoryError above 4 MB
        fs.read_chunks(path) -> iterator[bytes]  [loop f.read(1 << 20)]   any size
        fs.identity(path)    -> (dev, inode)     [os.stat: st_dev, st_ino]

    Symlinks are followed silently by list_dir / is_dir, so a tree can contain cycles.

Q0  LeetCode 609 — the walk is done for you.
    The input is directory-info strings "root/d1 f1.txt(content1) f2.txt(content2)"; return every group of
    files with identical content (each group of 2+, elements are full paths like root/d1/f1.txt).
    Parse, then group. The grouping half is what every later question reuses.

Q1  list_files(root, fs) -> list[str]
    Every file under root, any order. list_dir shows one level, so you write the loop that opens
    every directory. Plain trees only; recursion is fine here.

Q2  find_dups(root, fs) -> list[list[str]]
    Take Q1's list, read each file, group by content, keep groups of 2+. Each file once, order free.
    Reported: "key by content or by a hash of it" — the content itself is fine at this point.

Q3  "It crashed on a real machine. Why?"  — permissions.
    Some directories and files are unreadable: list_dir / read_file raise PermissionError.
    Skip that entry and keep going. Same two functions, now wrapped in try/except.

Q4  "Some files are gigabytes."  — too large to load.
    read_file raises MemoryError above 4 MB. Group by fs.size first (free), then hash with
    fs.read_chunks only inside same-size groups; a file with no size twin is never read.
    Q2's dict key changes from the content to the size, then the digest.

Q5  "A folder with thousands of children. A folder nested very deep. A symlink loop."  — the walk.
    Recursion dies near 1,000 frames: rewrite Q1 with an explicit container (queue = BFS, stack = DFS;
    say which and why). A symlink makes the same directory reachable twice: keep visited keyed by
    fs.identity, not by path, and list a file once even if two paths reach it.

HOW THE ANSWERS CHAIN
    Q0's group_by_content takes (path, content) pairs — Q2 feeds it pairs read from the disk instead of pairs
    parsed from strings · Q3 wraps the walk and the read in try/except · Q4 feeds it (path, digest) pairs,
    only for size twins · Q5 rewrites Q1's loop.
    Final shape:  list_files (Q1+Q3+Q5) -> group_by_size (Q4) -> group_by_content(hash_pairs(...)) (Q0+Q3+Q4)

Run:  python3 dupfinder.py          every question
      python3 dupfinder.py 3        one question (or several: 1 2)
"""
import contextlib
import hashlib
import io
import sys
import time
import traceback
from collections import deque

from fakefs import FakeFS

MB = 1024 * 1024


# =====================================================================================
#  TEST CASES — each builder returns (fs, root); a case says which function to call
# =====================================================================================
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
    return fs, "/docs"                        # only a.txt, b.txt and sub/c.txt are inside


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


def big_pairs():
    fs = FakeFS()
    fs.add_file("/big/a.bin", big=(1, 6 * MB))
    fs.add_file("/big/b.bin", big=(1, 6 * MB))   # same seed + size -> identical content
    fs.add_file("/big/c.bin", big=(2, 6 * MB))   # same size, different content
    fs.add_file("/big/d.bin", big=(3, 9 * MB))   # unique size: must never be read
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
    fs.deny("/m/c.bin")                          # a third twin, unreadable -> not in the group
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


def symlink_cycle():
    fs = FakeFS()
    fs.add_file("/a/f1", b"x")
    fs.add_file("/a/b/f2", b"x")
    fs.add_symlink("/a/b/loop", "/a")            # /a/b/loop/b/loop/b/... forever
    fs.add_symlink("/a/b/self", "/a/b")
    return fs, "/"


def symlink_to_sibling():
    fs = FakeFS()
    fs.add_file("/p/r/f", b"k")
    fs.add_file("/p/q/g", b"k")
    fs.add_symlink("/p/q/s", "/p/r")             # /p/r/f is also reachable as /p/q/s/f
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


def lc_example_1():
    return (["root/a 1.txt(abcd) 2.txt(efgh)", "root/c 3.txt(abcd)", "root/c/d 4.txt(efgh)", "root 4.txt(efgh)"],
            [["root/a/1.txt", "root/c/3.txt"], ["root/4.txt", "root/a/2.txt", "root/c/d/4.txt"]])


def lc_example_2():
    return (["root/a 1.txt(abcd) 2.txt(efgh)", "root/c 3.txt(abcd)", "root/c/d 4.txt(efgh)"],
            [["root/a/1.txt", "root/c/3.txt"], ["root/a/2.txt", "root/c/d/4.txt"]])


def lc_no_dups():
    return (["root/a 1.txt(a) 2.txt(b)", "root/b 3.txt(c)"], [])


# kind: "lc"      -> find_duplicate_609(paths)                                  checked as sorted groups
#       "files"   -> list_files(root, fs)                                        checked against every file the walk can reach
#       "content" -> group_by_content(read_pairs(list_files(root, fs), fs))      checked as groups
#       "dups"    -> find_dups(root, fs)                                          checked as groups
QUESTIONS = {
    0: ("LeetCode 609: the walk is done for you — parse the strings, group by content", [
        ("lc", "LC example 1", lc_example_1),
        ("lc", "LC example 2", lc_example_2),
        ("lc", "no duplicates -> []", lc_no_dups),
    ]),
    1: ("list every file under root (plain trees)", [
        ("files", "a tree three levels deep, with an empty dir", plain_tree),
        ("files", "empty root -> []", empty_root),
        ("files", "root is a subdirectory: only what is under it", root_is_a_subdir),
    ]),
    2: ("group Q1's files by content, keep groups of 2+", [
        ("content", "three groups' worth of files, through Q0's group_by_content", plain_tree),
        ("dups", "the same through find_dups", plain_tree),
        ("dups", "no duplicates -> []", no_dups),
        ("dups", "root is a subdirectory", root_is_a_subdir),
    ]),
    3: ("permissions: skip what you cannot open, keep going", [
        ("files", "unreadable directory: its subtree is absent, everything else listed", unreadable_dir),
        ("dups", "unreadable file: in no group, the rest still grouped", unreadable_file),
        ("dups", "unreadable directory: its files are in no group", unreadable_dir),
    ]),
    4: ("files too big to load: size first, chunked hash only on size twins", [
        ("dups", "6 MB twins + a same-size impostor + a 9 MB loner + two tiny twins", big_pairs),
        ("dups", "20 big files, 20 distinct sizes -> nothing should be read (watch the time)", big_all_unique_sizes),
        ("dups", "big twins where the third copy is unreadable", big_and_unreadable),
    ]),
    5: ("the walk meets the real disk: deep, wide, symlink cycles", [
        ("files", "a directory nested 2,000 deep (recursion dies here)", deep_chain),
        ("files", "5,000 files in one directory", wide_dir),
        ("files", "symlink cycle /a/b/loop -> /a: must terminate, each file once", symlink_cycle),
        ("files", "symlink to a sibling dir: one file reachable by two paths, listed once", symlink_to_sibling),
        ("dups", "everything at once", everything_at_once),
    ]),
}


# =====================================================================================
#  IMPLEMENTATION — in interview order. A later question redefines the function it changes,
#  so the last definition of each name is the one that runs. To practice question N, delete
#  its section and write it back.
# =====================================================================================

# ---------------- Q0: LeetCode 609 — the walk is done for you; parse, then group ----------------
def parse_609(paths):
    # "root/d1 f1.txt(content1) f2.txt(content2)" -> [(complete_path, file_content), ...]
    pairs = []
    for i in range(len(paths)):
        contents = paths[i].split(" ")
        file_path = contents[0]
        for j in range(1, len(contents)):
            file_string = contents[j].split("(")
            file_content = file_string[1].rstrip(")")
            file_name = file_string[0]
            complete_path = file_path + "/" + file_name
            pairs.append((complete_path, file_content))
    return pairs


def group_by_content(pairs):
    # (path, content) pairs -> groups of 2+. The content is the dict key, the paths are the value.
    # Every later question calls this one; only where the pairs come from changes.
    content_path_dict = {}
    for complete_path, file_content in pairs:
        if file_content not in content_path_dict:
            content_path_dict[file_content] = [complete_path]
        else:
            content_path_dict[file_content].append(complete_path)
    res = []
    for key, value in content_path_dict.items():
        if len(value) > 1:
            res.append(value)
    return res


def find_duplicate_609(paths):
    return group_by_content(parse_609(paths))


# ---------------- Q1: every file under root (recursion allowed here) ----------------
def list_files(root, fs):
    # list_dir shows one level, so: for each entry, a directory means "go in", a file means "collect"
    files = []
    for p in fs.list_dir(root):
        if fs.is_dir(p):
            files.extend(list_files(p, fs))
        else:
            files.append(p)
    return files


# ---------------- Q2: the walk replaces the string parsing; the grouping is Q0's ----------------
def read_pairs(paths, fs):
    # the real-disk version of parse_609: (path, content) pairs, content read from the file
    return [(p, fs.read_file(p)) for p in paths]


def find_dups(root, fs):
    return group_by_content(read_pairs(list_files(root, fs), fs))


# ---------------- Q3: permissions — the walk and the read, wrapped in try/except ----------------
def list_files(root, fs):                               # a directory that will not open is skipped, with its subtree
    files = []
    try:
        children = fs.list_dir(root)
    except OSError:                                     # PermissionError is an OSError
        return files
    for p in children:
        if fs.is_dir(p):
            files.extend(list_files(p, fs))
        else:
            files.append(p)
    return files


def read_pairs(paths, fs):                              # an unreadable file yields no pair, so it is in no group
    pairs = []
    for p in paths:
        try:
            pairs.append((p, fs.read_file(p)))
        except OSError:
            continue
    return pairs


# ---------------- Q4: too large to load — size first, then (path, digest) pairs into Q0's grouping ----------------
def group_by_size(paths, fs):
    # size is metadata, free to read; different sizes cannot be equal, so most files are never opened
    by_size = {}
    for p in paths:
        try:
            by_size.setdefault(fs.size(p), []).append(p)
        except OSError:
            continue
    return [g for g in by_size.values() if len(g) >= 2]


def hash_pairs(paths, fs):
    # read_pairs with a digest instead of the content: chunked, so the file's size does not matter; Q3's skip again
    pairs = []
    for p in paths:
        h = hashlib.sha256()
        try:
            for chunk in fs.read_chunks(p):
                h.update(chunk)
        except OSError:
            continue
        pairs.append((p, h.digest()))
    return pairs


def find_dups(root, fs):                                # "key by content or by a hash of it": same grouping, new key
    result = []
    for same_size in group_by_size(list_files(root, fs), fs):
        result.extend(group_by_content(hash_pairs(same_size, fs)))
    return result


# ---------------- Q5: deep, wide, symlink loops — the walk, iterative and keyed by identity ----------------
def list_files(root, fs):
    # explicit queue instead of recursion (BFS; a stack here would be DFS, same answer, different memory shape).
    # visited is keyed by fs.identity, not by path: a symlink makes one directory appear under a second path.
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
        except OSError:
            continue
        for p in children:
            if fs.is_dir(p):
                queue.append(p)
                continue
            try:
                ident = fs.identity(p)
            except OSError:                             # dangling symlink etc.
                continue
            if ident not in seen_files:                 # the same file reachable by two paths: once
                seen_files.add(ident)
                files.append(p)
    return files


# =====================================================================================
#  RUNNER
# =====================================================================================
GREEN, RED, YELLOW, BLUE, BOLD, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[94m", "\033[1m", "\033[0m"


def check_files(fs, root, got):
    expected = set(fs._truth(root, include_unreadable=True))          # inodes the walk can reach
    if not isinstance(got, list):
        return f"returned {type(got).__name__}, expected a list of paths"
    seen = set()
    for p in got:
        try:
            ino = fs.identity(p)[1]
        except Exception:
            return f"path does not exist: {p!r}"
        if ino in seen:
            return f"the same file appears twice: {p!r}"
        seen.add(ino)
    if seen == expected:
        return None
    path_of = {ino: path for ino, (key, path) in fs._truth(root, include_unreadable=True).items()}
    missing = sorted(path_of[i] for i in expected - seen)
    extra = [p for p in got if fs.identity(p)[1] not in expected]
    msg = f"expected {len(expected)} files, got {len(seen)}"
    if missing:
        msg += f"\n      missing: {missing[:4]}{' ...' if len(missing) > 4 else ''}"
    if extra:
        msg += f"\n      should not be listed: {extra[:4]}{' ...' if len(extra) > 4 else ''}"
    return msg


def check_groups(fs, root, got):
    truth = fs._truth(root)                                            # readable files only
    by_key = {}
    for ino, (key, path) in truth.items():
        by_key.setdefault(key, set()).add(ino)
    expected = {frozenset(s) for s in by_key.values() if len(s) >= 2}
    if not isinstance(got, list):
        return f"returned {type(got).__name__}, expected a list of lists"
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


def check_lc(expected, _paths, got):
    norm = lambda out: sorted(sorted(g) for g in out)
    if not isinstance(got, list):
        return f"returned {type(got).__name__}, expected a list of lists"
    if norm(got) == norm(expected):
        return None
    return f"expected {norm(expected)}\n      got      {norm(got)}"


CALLS = {
    "lc":      (lambda paths, _: find_duplicate_609(paths), check_lc),
    "files":   (lambda root, fs: list_files(root, fs), check_files),
    "content": (lambda root, fs: group_by_content(read_pairs(list_files(root, fs), fs)), check_groups),
    "dups":    (lambda root, fs: find_dups(root, fs), check_groups),
}
RUNNER_FRAMES = {"run_question", "main", "<lambda>", "<module>"}


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
    frames = [f for f in traceback.extract_tb(exc.__traceback__)
              if f.filename.endswith("dupfinder.py") and f.name not in RUNNER_FRAMES]
    where = f" at dupfinder.py:{frames[-1].lineno} in {frames[-1].name}()" if frames else ""
    if isinstance(exc, NotImplementedError):
        print(f"      {YELLOW}not implemented yet{RESET}")
    else:
        print(f"      {RED}{type(exc).__name__}: {str(exc)[:90]}{where}{RESET}")


def run_question(n):
    title, cases = QUESTIONS[n]
    print(f"\n{BLUE}{BOLD}Q{n} · {title}{RESET}")
    passed = 0
    for kind, name, build in cases:
        if kind == "lc":
            paths, expected = build()
            fs, root = expected, paths                  # check_lc(expected, got); the call gets (paths, _)
        else:
            fs, root = build()
        call, check = CALLS[kind]
        buf = io.StringIO()
        t0 = time.perf_counter()
        try:
            with contextlib.redirect_stdout(buf):
                got = call(root, fs)
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
    wanted = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(QUESTIONS)
    total_pass = total = 0
    for n in wanted:
        p, t = run_question(n)
        total_pass += p
        total += t
    color = GREEN if total_pass == total else RED
    print(f"\n{color}{BOLD}TOTAL {total_pass}/{total}{RESET}\n")


if __name__ == "__main__":
    main()
