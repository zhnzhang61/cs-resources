#!/usr/bin/env python3
"""
Excel: set_cell / get_cell

MAIN PROBLEM (as reported first-hand)

class Spreadsheet:
    set_cell(label, value) -> bool
    get_cell(label) -> int | None
    delete_cell(label) -> None

    label : uppercase letters + digits, e.g. "A1", "B10"
    value : an int, a decimal string ("10"), or a formula string starting
            with "=" — additions of non-negative ints and labels: "=B1+C1+1", "=1+2"

Scope 1  literals only: set / get; get of an unset cell -> None.
         (pass it fast — the reports say don't spend time here)

Scope 2  formulas. get_cell must be O(1): compute at set time and cache the
         value of every cell, so a get is one dictionary lookup. Simplest
         correct version: on every set, recompute every cell. A cell whose
         formula depends (directly or indirectly) on an unset cell has value
         None. Setting a cell again replaces its formula and dependencies.

Scope 3  cycle detection + delete. set_cell returns False and leaves the
         sheet unchanged if the new formula would create a cycle (including
         a cell referencing itself); otherwise returns True (scopes 1-2 may
         ignore the return value). delete_cell removes a cell: its
         dependents now see an unset cell (-> None); deleting an unset cell
         is a no-op. Optimization: on set, recompute only the cells that
         depend on the changed cell (keep reverse edges).

Advice from the field: make each scope run before starting the next.

FOLLOW-UP VARIANT (seen in aggregator write-ups): the same engine driven by
a command script.

    run(script) -> list[str]

    script : lines "SET label value" and "GET label", joined by "\\n"
    value  : a non-negative int, or an addition formula WITHOUT the "="
             prefix ("A1+A2+5")
    SET    -> "OK", or "ERROR" if it would create a cycle (sheet unchanged)
    GET    -> the value as a string, or "ERROR" if the cell is unset or
              depends on an unset cell
    Implement it as a thin adapter over Spreadsheet.

Run the tests:  python3 test_excel.py        (all scopes)
                python3 test_excel.py 2      (scope 2 only)
                python3 test_excel.py 4      (the follow-up variant)
or just run this file (F5 in VS Code).
"""


class Spreadsheet:
    def __init__(self):
        raise NotImplementedError

    def set_cell(self, label: str, value) -> bool:
        raise NotImplementedError

    def get_cell(self, label: str):
        raise NotImplementedError

    def delete_cell(self, label: str) -> None:
        raise NotImplementedError


def run(script: str) -> list[str]:
    raise NotImplementedError


if __name__ == "__main__":
    from test_excel import main
    main()
