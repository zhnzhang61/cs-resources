#!/usr/bin/env python3
"""Test harness for spreadsheet.py.

Usage:
    python3 test_spreadsheet.py          # run every part
    python3 test_spreadsheet.py 2        # run part 2 only
    python3 test_spreadsheet.py 1 3      # run parts 1 and 3
"""
import contextlib
import io
import sys
import traceback

from spreadsheet import run

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def deep_chain(n):
    lines = ["SET A1 1"] + [f"SET A{i} A{i-1}+1" for i in range(2, n + 1)] + [f"GET A{n}"]
    return "\n".join(lines), ["OK"] * n + [str(n)]


PARTS = {
    1: ("literals: SET / GET / parsing", [
        ("set then get",
         "SET A1 10\nGET A1",
         ["OK", "10"]),
        ("get an unset cell",
         "GET A1",
         ["ERROR"]),
        ("overwrite a literal",
         "SET A1 5\nSET A1 7\nGET A1",
         ["OK", "OK", "7"]),
        ("zero value, two-digit row",
         "SET B10 0\nGET B10",
         ["OK", "0"]),
        ("two-letter column is a different cell",
         "SET AA1 3\nGET AA1\nGET A1",
         ["OK", "3", "ERROR"]),
    ]),
    2: ("formulas: references + evaluation", [
        ("chain (official example 1)",
         "SET A1 10\nGET A1\nSET A2 A1+20\nGET A2\nSET A3 A1+A2+5\nGET A3",
         ["OK", "10", "OK", "30", "OK", "45"]),
        ("formula of literals only",
         "SET A1 1+2+3\nGET A1",
         ["OK", "6"]),
        ("diamond: one cell reached by two paths is legal",
         "SET A1 1\nSET B1 A1+1\nSET C1 A1+B1\nGET C1",
         ["OK", "OK", "OK", "3"]),
        ("same cell twice in one formula",
         "SET A1 2\nSET B1 A1+A1\nGET B1",
         ["OK", "OK", "4"]),
        ("GET reflects the latest upstream value",
         "SET A1 10\nSET A2 A1+1\nGET A2\nSET A1 20\nGET A2",
         ["OK", "OK", "11", "OK", "21"]),
        ("formula replaced by a literal stops following upstream",
         "SET A1 1\nSET A2 A1+1\nSET A2 100\nSET A1 50\nGET A2",
         ["OK", "OK", "OK", "OK", "100"]),
        ("unset dependency: SET is OK, GET errors until it is filled",
         "SET A2 A1+1\nGET A2\nSET A1 1\nGET A2",
         ["OK", "ERROR", "OK", "2"]),
        ("unset two levels down",
         "SET A2 A1+1\nSET A3 A2+1\nGET A3",
         ["OK", "OK", "ERROR"]),
    ]),
    3: ("cycles: reject and leave the sheet unchanged", [
        ("cycle rejected, old values kept (official example 2)",
         "SET A1 10\nSET B1 A1+1\nSET A1 B1+1\nGET A1\nGET B1",
         ["OK", "OK", "ERROR", "10", "11"]),
        ("self-reference on an unset cell",
         "SET A1 A1+1\nGET A1",
         ["ERROR", "ERROR"]),
        ("self-reference keeps the old value",
         "SET A1 5\nSET A1 A1+1\nGET A1",
         ["OK", "ERROR", "5"]),
        ("three-cell cycle, then the sheet still works",
         "SET A1 B1+1\nSET B1 C1+1\nSET C1 A1+1\nGET A1\nSET C1 7\nGET A1",
         ["OK", "OK", "ERROR", "ERROR", "OK", "9"]),
        ("cycle that runs through unset cells",
         "SET A1 B1+1\nSET B1 A1+1\nGET B1",
         ["OK", "ERROR", "ERROR"]),
        ("overwrite removes the old edge, so no cycle anymore",
         "SET A1 B1+1\nSET A1 5\nSET B1 A1+1\nGET B1",
         ["OK", "OK", "OK", "6"]),
    ]),
    4: ("bonus: deep chain (Python's default recursion limit is ~1000)", [
        ("chain of 3000 cells",) + deep_chain(3000),
    ]),
}


def show_diff(script, expected, got):
    commands = script.split("\n")
    if not isinstance(got, list):
        print(f"      {RED}run() returned {type(got).__name__}, expected list{RESET}")
        return
    if len(got) != len(expected):
        print(f"      {YELLOW}length: expected {len(expected)} results, got {len(got)}{RESET}")
    shown = 0
    for i in range(max(len(expected), len(got))):
        e = expected[i] if i < len(expected) else "<missing>"
        g = got[i] if i < len(got) else "<missing>"
        if e != g:
            cmd = commands[i] if i < len(commands) else "?"
            print(f"      line {i+1:<5} {cmd:<22} expected {e!r:<10} got {g!r}")
            shown += 1
            if shown == 3:
                print("      ... (first 3 mismatches only)")
                break


def show_exception(exc):
    frames = traceback.extract_tb(exc.__traceback__)
    mine = [f for f in frames if f.filename.endswith("spreadsheet.py") and not f.filename.endswith("test_spreadsheet.py")]
    where = f" at spreadsheet.py:{mine[-1].lineno} in {mine[-1].name}()" if mine else ""
    if isinstance(exc, NotImplementedError):
        print(f"      {YELLOW}not implemented yet{RESET}")
    else:
        print(f"      {RED}{type(exc).__name__}: {str(exc)[:80]}{where}{RESET}")


def show_prints(text, limit=15):
    if not text:
        return
    lines = text.rstrip("\n").split("\n")
    print(f"      {YELLOW}your prints:{RESET}")
    for ln in lines[:limit]:
        print(f"      │ {ln}")
    if len(lines) > limit:
        print(f"      │ ... ({len(lines) - limit} more lines)")


def run_part(n):
    title, cases = PARTS[n]
    print(f"\n{BLUE}{BOLD}Part {n} · {title}{RESET}")
    passed = 0
    for name, script, expected in cases:
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                got = run(script)
        except BaseException as exc:
            if isinstance(exc, KeyboardInterrupt):
                raise
            print(f"  {RED}✗{RESET} {name}")
            show_prints(buf.getvalue())
            show_exception(exc)
            continue
        if got == expected:
            print(f"  {GREEN}✓{RESET} {name}")
            show_prints(buf.getvalue())
            passed += 1
        else:
            print(f"  {RED}✗{RESET} {name}")
            show_prints(buf.getvalue())
            show_diff(script, expected, got)
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
