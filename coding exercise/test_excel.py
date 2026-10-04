#!/usr/bin/env python3
"""Test harness for excel.py.

Usage:
    python3 test_excel.py          # run every scope
    python3 test_excel.py 2        # run scope 2 only
    python3 test_excel.py 1 3      # run scopes 1 and 3

Scopes 1-3 (main problem): a case is a list of operations applied to a fresh
Spreadsheet():  ("set", label, value)  ("get", label)  ("del", label)
Scopes 1-2 record only the results of gets; scope 3 also records what
set_cell returns (True / False).

Scope 4 (follow-up variant): a case is a command script string passed to run();
each line yields exactly what the method call returned (True/False, int/None, None).
"""
import contextlib
import io
import sys
import time
import traceback

import excel
from excel import run
Spreadsheet = getattr(excel, "Spreadsheet", None) or excel.SpreadSheet      # either spelling works

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_ops(ops, record_set=False):
    if isinstance(ops, str):                    # scope 4: command script
        return run(ops)
    sh = Spreadsheet()
    out = []
    for op in ops:
        if op[0] == "set":
            r = sh.set_cell(op[1], op[2])
            if record_set:
                out.append(r)
        elif op[0] == "get":
            out.append(sh.get_cell(op[1]))
        elif op[0] == "del":
            (getattr(sh, "delete_cell", None) or sh.del_cell)(op[1])   # either name works
    return out


def chain_then_gets(n, gets):
    ops = [("set", "A1", "1")] + [("set", f"A{i}", f"=A{i-1}+1") for i in range(2, n + 1)]
    ops += [("get", f"A{n}")] * gets
    return ops, [n] * gets


def chain_then_independent_sets(n):
    ops = [("set", "A1", "1")] + [("set", f"A{i}", f"=A{i-1}+1") for i in range(2, n + 1)]
    ops += [("set", f"B{i}", str(i)) for i in range(1, n + 1)]          # no dependents at all
    ops += [("get", f"A{n}"), ("get", "B7")]
    return ops, [True] * (2 * n) + [n, 7]        # scope 3 records every set's True/False


def script_chain(n):
    lines = ["SET A1 1"] + [f"SET A{i} =A{i-1}+1" for i in range(2, n + 1)] + [f"GET A{n}"]
    return "\n".join(lines), [True] * n + [n]


SCOPES = {
    1: ("literals: set / get", [
        ("set then get", [("set", "A1", "10"), ("get", "A1")], [10]),
        ("get of an unset cell -> None", [("get", "A1")], [None]),
        ("overwrite", [("set", "A1", "5"), ("set", "A1", "7"), ("get", "A1")], [7]),
        ("literal given as a string (one report's format)", [("set", "A1", "10"), ("get", "A1")], [10]),
        ("zero and a two-letter column", [("set", "AA10", "0"), ("get", "AA10"), ("get", "A10")], [0, None]),
    ]),
    2: ("formulas, cached so that get is one lookup", [
        ("formula of literals only", [("set", "A1", "=1+2"), ("get", "A1")], [3]),
        ("references plus a literal",
         [("set", "A1", "1"), ("set", "B1", "2"), ("set", "C1", "=A1+B1+1"), ("get", "C1")], [4]),
        ("a later set propagates to the dependent",
         [("set", "A1", "1"), ("set", "B1", "=A1+1"), ("get", "B1"), ("set", "A1", "10"), ("get", "B1")], [2, 11]),
        ("nested references, update the root",
         [("set", "A1", "1"), ("set", "B1", "=A1+1"), ("set", "C1", "=B1+1"), ("set", "D1", "=C1+1"),
          ("get", "D1"), ("set", "A1", "100"), ("get", "D1")], [4, 103]),
        ("one cell referenced by three others",
         [("set", "A1", "1"), ("set", "B1", "=A1+1"), ("set", "C1", "=A1+2"), ("set", "D1", "=A1+3"),
          ("set", "A1", "10"), ("get", "B1"), ("get", "C1"), ("get", "D1")], [11, 12, 13]),
        ("same cell twice in one formula",
         [("set", "A1", "2"), ("set", "B1", "=A1+A1"), ("get", "B1")], [4]),
        ("formula replaced by a literal stops following upstream",
         [("set", "A1", "1"), ("set", "B1", "=A1+1"), ("set", "B1", "100"), ("set", "A1", "50"), ("get", "B1")], [100]),
        ("formula replaced by another formula drops the old edge",
         [("set", "A1", "1"), ("set", "C1", "5"), ("set", "B1", "=A1+1"), ("set", "B1", "=C1+1"),
          ("set", "A1", "99"), ("get", "B1")], [6]),
        ("unset dependency -> None, then it appears",
         [("set", "B1", "=A1+1"), ("get", "B1"), ("set", "A1", "1"), ("get", "B1")], [None, 2]),
        ("unset two levels down -> None",
         [("set", "B1", "=A1+1"), ("set", "C1", "=B1+1"), ("get", "C1")], [None]),
        ("bonus timing: 500-cell chain then 20,000 gets (lazy recompute = seconds, cache = instant)",
         *chain_then_gets(500, 20_000)),
    ]),
    3: ("cycle detection + delete (set returns True / False)", [
        ("cycle rejected, old values kept",
         [("set", "A1", "10"), ("set", "B1", "=A1+1"), ("set", "A1", "=B1+1"), ("get", "A1"), ("get", "B1")],
         [True, True, False, 10, 11]),
        ("self reference", [("set", "A1", "=A1+1"), ("get", "A1")], [False, None]),
        ("self reference keeps the old literal", [("set", "A1", "5"), ("set", "A1", "=A1+1"), ("get", "A1")], [True, False, 5]),
        ("three-cell cycle through unset cells",
         [("set", "A1", "=B1+1"), ("set", "B1", "=C1+1"), ("set", "C1", "=A1+1"), ("get", "A1"), ("set", "C1", "7"), ("get", "A1")],
         [True, True, False, None, True, 9]),
        ("overwrite removes the old edge, so no cycle anymore",
         [("set", "A1", "=B1+1"), ("set", "A1", "5"), ("set", "B1", "=A1+1"), ("get", "B1")],
         [True, True, True, 6]),
        ("delete a referenced cell -> dependents see None, then set it back",
         [("set", "A1", "5"), ("set", "B1", "=A1+1"), ("get", "B1"), ("del", "A1"), ("get", "B1"), ("get", "A1"),
          ("set", "A1", "2"), ("get", "B1")],
         [True, True, 6, None, None, True, 3]),
        ("delete an unset cell is a no-op", [("del", "Z9"), ("get", "Z9")], [None]),
        ("delete then a formula into the gap may be set again",
         [("set", "A1", "1"), ("set", "B1", "=A1+1"), ("del", "B1"), ("set", "B1", "=A1+2"), ("get", "B1")],
         [True, True, True, 3]),
        ("bonus timing: 1,500-cell chain, then 1,500 unrelated sets (recompute-all = seconds, dependents-only = instant)",
         *chain_then_independent_sets(1_500)),
    ]),
    4: ("follow-up variant: run(script), one method call per line, results passed through", [
        ("set then get", "SET A1 10\nGET A1", [True, 10]),
        ("get an unset cell", "GET A1", [None]),
        ("overwrite a literal", "SET A1 5\nSET A1 7\nGET A1", [True, True, 7]),
        ("zero value, two-digit row", "SET B10 0\nGET B10", [True, 0]),
        ("two-letter column is a different cell", "SET AA1 3\nGET AA1\nGET A1", [True, 3, None]),
        ("chain of three cells",
         "SET A1 10\nGET A1\nSET A2 =A1+20\nGET A2\nSET A3 =A1+A2+5\nGET A3",
         [True, 10, True, 30, True, 45]),
        ("formula of literals only", "SET A1 =1+2+3\nGET A1", [True, 6]),
        ("diamond: one cell reached by two paths is legal",
         "SET A1 1\nSET B1 =A1+1\nSET C1 =A1+B1\nGET C1", [True, True, True, 3]),
        ("same cell twice in one formula", "SET A1 2\nSET B1 =A1+A1\nGET B1", [True, True, 4]),
        ("GET reflects the latest upstream value",
         "SET A1 10\nSET A2 =A1+1\nGET A2\nSET A1 20\nGET A2", [True, True, 11, True, 21]),
        ("formula replaced by a literal stops following upstream",
         "SET A1 1\nSET A2 =A1+1\nSET A2 100\nSET A1 50\nGET A2", [True, True, True, True, 100]),
        ("unset dependency: SET succeeds, GET is None until it is filled",
         "SET A2 =A1+1\nGET A2\nSET A1 1\nGET A2", [True, None, True, 2]),
        ("unset two levels down", "SET A2 =A1+1\nSET A3 =A2+1\nGET A3", [True, True, None]),
        ("cycle rejected, old values kept",
         "SET A1 10\nSET B1 =A1+1\nSET A1 =B1+1\nGET A1\nGET B1", [True, True, False, 10, 11]),
        ("self-reference on an unset cell", "SET A1 =A1+1\nGET A1", [False, None]),
        ("self-reference keeps the old value", "SET A1 5\nSET A1 =A1+1\nGET A1", [True, False, 5]),
        ("three-cell cycle, then the sheet still works",
         "SET A1 =B1+1\nSET B1 =C1+1\nSET C1 =A1+1\nGET A1\nSET C1 7\nGET A1",
         [True, True, False, None, True, 9]),
        ("cycle that runs through unset cells", "SET A1 =B1+1\nSET B1 =A1+1\nGET B1", [True, False, None]),
        ("overwrite removes the old edge, so no cycle anymore",
         "SET A1 =B1+1\nSET A1 5\nSET B1 =A1+1\nGET B1", [True, True, True, 6]),
        ("DELETE: the dependent goes back to None",
         "SET A1 1\nSET B1 =A1+1\nGET B1\nDELETE A1\nGET B1\nGET A1", [True, True, 2, None, None, None]),
        ("DELETE an unset cell is a no-op", "DELETE Z9\nGET Z9", [None, None]),
        ("DELETE then SET the same cell again",
         "SET A1 1\nSET B1 =A1+1\nDELETE B1\nSET B1 =A1+2\nGET B1", [True, True, None, True, 3]),
        ("DELETE removes the cell's edges, so the reverse formula is no longer a cycle",
         "SET A1 1\nSET B1 =A1+1\nDELETE B1\nSET A1 =B1+1\nGET A1", [True, True, None, True, None]),
        ("chain of 3,000 cells (Python's default recursion limit is ~1,000)", *script_chain(3000)),
    ]),
}


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
    mine = [f for f in frames if f.filename.endswith("excel.py") and not f.filename.endswith("test_excel.py")]
    where = f" at excel.py:{mine[-1].lineno} in {mine[-1].name}()" if mine else ""
    if isinstance(exc, NotImplementedError):
        print(f"      {YELLOW}not implemented yet{RESET}")
    else:
        print(f"      {RED}{type(exc).__name__}: {str(exc)[:80]}{where}{RESET}")


def show_diff(ops, expected, got, record_set):
    if not isinstance(got, list):
        print(f"      {RED}returned {type(got).__name__}, expected list{RESET}")
        return
    if isinstance(ops, str):
        recorded = ops.split("\n")
    else:
        recorded = [" ".join(str(x) for x in op) for op in ops if op[0] == "get" or (record_set and op[0] == "set")]
    if len(got) != len(expected):
        print(f"      {YELLOW}length: expected {len(expected)} results, got {len(got)}{RESET}")
    shown = 0
    for i in range(max(len(expected), len(got))):
        e = expected[i] if i < len(expected) else "<missing>"
        g = got[i] if i < len(got) else "<missing>"
        if e != g:
            op = recorded[i] if i < len(recorded) else "?"
            print(f"      step {i+1:<4} {op:<24} expected {e!r:<8} got {g!r}")
            shown += 1
            if shown == 3:
                print("      ... (first 3 mismatches only)")
                break


def run_scope(n):
    title, cases = SCOPES[n]
    record_set = (n == 3)
    print(f"\n{BLUE}{BOLD}Scope {n} · {title}{RESET}")
    passed = 0
    for name, ops, expected in cases:
        buf = io.StringIO()
        t0 = time.perf_counter()
        try:
            with contextlib.redirect_stdout(buf):
                got = run_ops(ops, record_set)
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
            show_diff(ops, expected, got, record_set)
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
