#!/usr/bin/env python3
"""Test harness for retrieval.py.

Usage:
    python3 test_retrieval.py          # run every part
    python3 test_retrieval.py 2        # run part 2 only
    python3 test_retrieval.py 1 3      # run parts 1 and 3
"""
import contextlib
import io
import math
import random
import sys
import traceback

import retrieval as R

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ---- an independent reference used only to build expected answers for the big random case
def _ref_cosine(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return 0.0 if na == 0 or nb == 0 else sum(x * y for x, y in zip(a, b)) / (na * nb)


def _random_case(seed, n, d, k):
    rng = random.Random(seed)
    q = [rng.uniform(-1, 1) for _ in range(d)]
    docs = [[rng.uniform(-1, 1) for _ in range(d)] for _ in range(n)]
    order = sorted(range(n), key=lambda i: (-_ref_cosine(q, docs[i]), i))
    return (q, docs, k), order[:k]


_big_args, _big_expected = _random_case(seed=7, n=500, d=6, k=7)

# each case: (name, zero-arg callable that runs YOUR code, expected value)
PARTS = {
    1: ("cosine similarity", [
        ("identical vectors -> 1.0",
         lambda: R.cosine([3, 4], [3, 4]), 1.0),
        ("same direction, different length -> still 1.0 (cosine ignores length)",
         lambda: R.cosine([1, 2], [2, 4]), 1.0),
        ("orthogonal -> 0.0",
         lambda: R.cosine([1, 0], [0, 1]), 0.0),
        ("opposite -> -1.0",
         lambda: R.cosine([1, 0], [-1, 0]), -1.0),
        ("a real number in between: [3,4]·[4,3] = 24, norms 5 and 5",
         lambda: R.cosine([3, 4], [4, 3]), 0.96),
        ("45 degrees -> 1/sqrt(2)",
         lambda: R.cosine([1, 1], [1, 0]), 1 / math.sqrt(2)),
        ("zero vector -> 0.0 by convention (no ZeroDivisionError)",
         lambda: R.cosine([0, 0], [1, 2]), 0.0),
        ("three dimensions",
         lambda: R.cosine([1, 2, 3], [4, 5, 6]), 32 / (math.sqrt(14) * math.sqrt(77))),
    ]),
    2: ("top-k with a heap (ties -> smaller index)", [
        ("card example 1: equal cosine -> smaller index first",
         lambda: R.top_k([1, 0], [[1, 0], [0, 1], [2, 0]], 2), [0, 2]),
        ("card example 2",
         lambda: R.top_k([1, 1], [[1, 0], [0, 1]], 1), [0]),
        ("descending order, including negatives",
         lambda: R.top_k([1, 0], [[-1, 0], [0, 1], [1, 1]], 3), [2, 1, 0]),
        ("k larger than the corpus -> everything, still ordered",
         lambda: R.top_k([1, 0], [[0, 1], [1, 0]], 5), [1, 0]),
        ("k == 0 -> empty list",
         lambda: R.top_k([1, 0], [[1, 0]], 0), []),
        ("a zero doc scores 0.0 and ranks below a positive match",
         lambda: R.top_k([1, 0], [[0, 0], [1, 0]], 2), [1, 0]),
        ("all docs tie -> index order",
         lambda: R.top_k([1, 0], [[2, 0], [1, 0], [5, 0]], 3), [0, 1, 2]),
        ("500 random docs, k=7, checked against a brute-force sort",
         lambda: R.top_k(*_big_args), _big_expected),
    ]),
    3: ("precision@k and recall@k", [
        ("5 shown, 2 of them right, 3 relevant exist -> P 2/5, R 2/3",
         lambda: R.precision_recall_at_k([3, 1, 4, 0, 5], {1, 4, 9}, 5), (0.4, 2 / 3)),
        ("same list, k=3 -> both 2/3 (only the first 3 count)",
         lambda: R.precision_recall_at_k([3, 1, 4, 0, 5], {1, 4, 9}, 3), (2 / 3, 2 / 3)),
        ("one relevant doc, ranked first, k=1 -> P 1.0, R 1.0",
         lambda: R.precision_recall_at_k([7, 2, 5, 8, 6], {7}, 1), (1.0, 1.0)),
        ("same, k=5 -> precision falls to 0.2, recall stays 1.0",
         lambda: R.precision_recall_at_k([7, 2, 5, 8, 6], {7}, 5), (0.2, 1.0)),
        ("10 relevant exist, 5 shown all right -> P 1.0, R 0.5",
         lambda: R.precision_recall_at_k([0, 1, 2, 3, 4], set(range(10)), 5), (1.0, 0.5)),
        ("no hits -> 0.0, 0.0",
         lambda: R.precision_recall_at_k([5, 6], {1, 2}, 2), (0.0, 0.0)),
        ("fewer retrieved than k: precision still divides by k",
         lambda: R.precision_recall_at_k([1, 2], {1, 2, 3}, 5), (0.4, 2 / 3)),
        ("empty relevant set -> recall 0.0 by convention",
         lambda: R.precision_recall_at_k([1, 2], set(), 2), (0.0, 0.0)),
    ]),
    4: ("end to end: retrieve, then score", [
        ("toy corpus, k=3",
         lambda: R.evaluate_retrieval(
             [1, 0, 0],
             [[1, 0, 0], [0.9, 0.1, 0], [0, 1, 0], [0, 0, 1], [0.7, 0.7, 0], [-1, 0, 0]],
             {0, 1, 2}, 3),
         (2 / 3, 2 / 3)),
        ("same corpus, k=5 -> recall climbs, precision drops",
         lambda: R.evaluate_retrieval(
             [1, 0, 0],
             [[1, 0, 0], [0.9, 0.1, 0], [0, 1, 0], [0, 0, 1], [0.7, 0.7, 0], [-1, 0, 0]],
             {0, 1, 2}, 5),
         (0.6, 1.0)),
    ]),
}


def close(got, expected, tol=1e-9):
    if isinstance(expected, (list, tuple)):
        if not isinstance(got, (list, tuple)) or len(got) != len(expected):
            return False
        return all(close(g, e, tol) for g, e in zip(got, expected))
    if isinstance(expected, float) or isinstance(got, float):
        return isinstance(got, (int, float)) and abs(got - expected) <= tol
    return got == expected


def fmt(x):
    if isinstance(x, float):
        return f"{x:.6g}"
    if isinstance(x, (list, tuple)) and len(x) > 12:
        return f"{type(x).__name__} of {len(x)}: {x[:6]} ..."
    if isinstance(x, (list, tuple)):
        return "(" + ", ".join(fmt(v) for v in x) + ")" if isinstance(x, tuple) else "[" + ", ".join(fmt(v) for v in x) + "]"
    return repr(x)


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
    mine = [f for f in frames if f.filename.endswith("retrieval.py") and not f.filename.endswith("test_retrieval.py")]
    where = f" at retrieval.py:{mine[-1].lineno} in {mine[-1].name}()" if mine else ""
    if isinstance(exc, NotImplementedError):
        print(f"      {YELLOW}not implemented yet{RESET}")
    else:
        print(f"      {RED}{type(exc).__name__}: {str(exc)[:80]}{where}{RESET}")


def run_part(n):
    title, cases = PARTS[n]
    print(f"\n{BLUE}{BOLD}Part {n} · {title}{RESET}")
    passed = 0
    for name, call, expected in cases:
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                got = call()
        except BaseException as exc:
            if isinstance(exc, KeyboardInterrupt):
                raise
            print(f"  {RED}✗{RESET} {name}")
            show_prints(buf.getvalue())
            show_exception(exc)
            continue
        if close(got, expected):
            print(f"  {GREEN}✓{RESET} {name}")
            show_prints(buf.getvalue())
            passed += 1
        else:
            print(f"  {RED}✗{RESET} {name}")
            show_prints(buf.getvalue())
            print(f"      expected {fmt(expected)}")
            print(f"      got      {fmt(got)}")
    color = GREEN if passed == len(cases) else RED
    print(f"  {color}{passed}/{len(cases)} passed{RESET}")
    return passed, len(cases)


def main():
    wanted = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(PARTS)
    total_pass = total = 0
    for n in wanted:
        p, t = run_part(n)
        total_pass += p
        total += t
    color = GREEN if total_pass == total else RED
    print(f"\n{color}{BOLD}TOTAL {total_pass}/{total}{RESET}\n")


if __name__ == "__main__":
    main()
