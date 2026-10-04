#!/usr/bin/env python3
"""Test harness for highlight.py.

Usage:
    python3 test_highlight.py          # run every part
    python3 test_highlight.py 3        # run part 3 only
    python3 test_highlight.py 1 2      # run parts 1 and 2
"""
import contextlib
import io
import random
import sys
import time
import traceback

from highlight import highlight

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ---- independent reference, used only to build the expected answer of the big case
def _ref_highlight(text, sources):
    words = text.split(" ")
    first = {}
    for i, w in enumerate(words):
        first.setdefault(w, []).append(i)
    spans = []
    for src in sources:
        sw = src.split(" ")
        for i in first.get(sw[0], []):
            if words[i:i + len(sw)] == sw:
                spans.append((i, i + len(sw) - 1))
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    out, pos = [], 0
    for a, b in merged:
        out.extend(words[pos:a])
        out.append("<hl>" + " ".join(words[a:b + 1]) + "</hl>")
        pos = b + 1
    out.extend(words[pos:])
    return " ".join(out)


def _big_case(seed, n_words, n_sources, vocab=300):
    rng = random.Random(seed)
    words = [f"w{rng.randrange(vocab)}" for _ in range(n_words)]
    text = " ".join(words)
    sources = []
    for _ in range(n_sources):
        if rng.random() < 0.8:                       # phrases copied from the text, 1-4 words
            i = rng.randrange(n_words - 4)
            sources.append(" ".join(words[i:i + rng.randint(1, 4)]))
        else:                                        # phrases that match nothing
            sources.append(" ".join(f"x{rng.randrange(50)}" for _ in range(rng.randint(1, 3))))
    return (text, sources), _ref_highlight(text, sources)


_big_args, _big_expected = _big_case(seed=11, n_words=20_000, n_sources=2_000)
_mid_args, _mid_expected = _big_case(seed=5, n_words=2_000, n_sources=200)

# each case: (name, zero-arg callable that runs YOUR code, expected value)
PARTS = {
    1: ("one source: whole-word match + wrap", [
        ("single word, single occurrence",
         lambda: highlight("the quick brown fox", ["quick"]),
         "the <hl>quick</hl> brown fox"),
        ("two-word source",
         lambda: highlight("the quick brown fox", ["quick brown"]),
         "the <hl>quick brown</hl> fox"),
        ("source at the very start and the very end",
         lambda: highlight("fox eats fox", ["fox"]),
         "<hl>fox</hl> eats <hl>fox</hl>"),
        ("non-adjacent occurrences stay separate",
         lambda: highlight("a b a", ["a"]),
         "<hl>a</hl> b <hl>a</hl>"),
        ("whole-word: 'aa' must NOT match inside 'aaab'",
         lambda: highlight("aa aaab x", ["aa"]),
         "<hl>aa</hl> aaab x"),
        ("the reported example: 'blue' must not match inside 'blueprint'",
         lambda: highlight("blue sky and blueprint", ["blue"]),
         "<hl>blue</hl> sky and blueprint"),
        ("case-sensitive: 'The' is not 'the'",
         lambda: highlight("The cat the hat", ["the"]),
         "The cat <hl>the</hl> hat"),
        ("no match -> text unchanged",
         lambda: highlight("a b c", ["x"]),
         "a b c"),
        ("source longer than the text -> unchanged",
         lambda: highlight("a b", ["a b c"]),
         "a b"),
        ("the whole text is the source",
         lambda: highlight("a b c", ["a b c"]),
         "<hl>a b c</hl>"),
    ]),
    2: ("several sources, no overlaps between them", [
        ("two sources, two regions",
         lambda: highlight("the quick brown fox jumps", ["quick", "jumps"]),
         "the <hl>quick</hl> brown fox <hl>jumps</hl>"),
        ("one source matches nothing, the other still works",
         lambda: highlight("the quick brown fox", ["zebra", "brown"]),
         "the quick <hl>brown</hl> fox"),
        ("the same source listed twice -> still one tag",
         lambda: highlight("the quick brown fox", ["quick", "quick"]),
         "the <hl>quick</hl> brown fox"),
        ("adjacent regions (no shared word) stay separate",
         lambda: highlight("a b c d", ["a b", "c d"]),
         "<hl>a b</hl> <hl>c d</hl>"),
        ("sources given in an order different from their position in text",
         lambda: highlight("a b c d e", ["e", "a"]),
         "<hl>a</hl> b c d <hl>e</hl>"),
    ]),
    3: ("overlapping sources: merge into maximal regions", [
        ("card example: shared word -> one region",
         lambda: highlight("the quick brown fox", ["the quick", "quick brown"]),
         "<hl>the quick brown</hl> fox"),
        ("one source inside another",
         lambda: highlight("the quick brown fox", ["quick brown fox", "brown"]),
         "the <hl>quick brown fox</hl>"),
        ("transitive chain: A-B overlap, B-C overlap, A-C do not touch",
         lambda: highlight("a b c d e f", ["a b", "b c d", "d e"]),
         "<hl>a b c d e</hl> f"),
        ("identical spans from two sources -> one tag",
         lambda: highlight("a b c", ["b", "b"]),
         "a <hl>b</hl> c"),
        ("merge in one place, stay separate in another",
         lambda: highlight("a b c x a b", ["a b", "b c"]),
         "<hl>a b c</hl> x <hl>a b</hl>"),
        ("2,000 words x 200 sources, checked against a reference",
         lambda: highlight(*_mid_args), _mid_expected),
    ]),
    4: ("bonus: scale (naive n*L is ~seconds; target well under 1 s)", [
        ("20,000 words x 2,000 sources",
         lambda: highlight(*_big_args), _big_expected),
    ]),
}


def show_diff(expected, got):
    if not isinstance(got, str):
        print(f"      {RED}returned {type(got).__name__}, expected str{RESET}")
        return
    if len(expected) > 200:
        k = next((i for i, (a, b) in enumerate(zip(expected, got)) if a != b), min(len(expected), len(got)))
        print(f"      first difference at char {k}")
        print(f"      expected ...{expected[max(0, k-40):k+40]!r}...")
        print(f"      got      ...{got[max(0, k-40):k+40]!r}...")
    else:
        print(f"      expected {expected!r}")
        print(f"      got      {got!r}")


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
    mine = [f for f in frames if f.filename.endswith("highlight.py") and not f.filename.endswith("test_highlight.py")]
    where = f" at highlight.py:{mine[-1].lineno} in {mine[-1].name}()" if mine else ""
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
        t0 = time.perf_counter()
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
        elapsed = time.perf_counter() - t0
        timing = f"  {YELLOW}({elapsed:.2f} s){RESET}" if elapsed > 0.05 else ""
        if got == expected:
            print(f"  {GREEN}✓{RESET} {name}{timing}")
            show_prints(buf.getvalue())
            passed += 1
        else:
            print(f"  {RED}✗{RESET} {name}{timing}")
            show_prints(buf.getvalue())
            show_diff(expected, got)
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
