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

Scope 1  literals only: set / get; get of an unset cell -> None; set_cell
         returns True. (pass it fast — the reports say don't spend time here)

Scope 2  formulas: a cell may reference other cells. Values are computed
         when a cell is set, so get_cell is one lookup (the interviewer said
         so; simplest: on every set, recompute every cell). A cell whose
         formula depends (directly or indirectly) on an unset cell has value
         None; setting a cell again replaces its formula.

Scope 3  cycle detection + delete. set_cell returns False and leaves the
         sheet unchanged if the new formula would create a cycle (including
         a cell referencing itself); otherwise returns True. delete_cell
         removes a cell and returns None: its dependents now see an unset
         cell (-> None); deleting an unset cell is a no-op.

FOLLOW-UPS (only when asked)
    - chains of thousands of cells: recursion dies near 1,000 frames, go iterative.
    - recompute only the cells that depend on the changed cell (keep reverse edges).
    The second class below (SpreadSheetCached: explicit-stack evaluate) answers the first.

Advice from the field: make each scope run before starting the next.

FOLLOW-UP VARIANT: the same engine driven by a command script, one method
call per line.

    run(script) -> list

    script : lines "SET label value", "GET label" and "DELETE label",
             joined by "\\n"
    value  : exactly what set_cell takes, as text: "10" or "=A1+A2+5"
             (the "=" stays)
    Each line yields what the method call returned, in order:
        SET    -> True, or False if it would create a cycle (sheet unchanged)
        GET    -> the int, or None if the cell is unset or depends on one
        DELETE -> None
    So run() is pure dispatch: split the line, call the method, append.
    (Some write-ups phrase the output as strings — "OK"/"ERROR" and numbers
    as text, no "=" in formulas; that is the version on the web page's card
    and a three-line translation inside the adapter.)

Run the tests:  python3 test_excel.py        (all scopes)
                python3 test_excel.py 2      (scope 2 only)
                python3 test_excel.py 4      (the follow-up variant)
or just run this file (F5 in VS Code).
"""

class Spreadsheet:
    """Parts 1-3 the way a first sitting writes them. Values are computed at set time, so get is one lookup.
    Part 1: store + look up. Part 2: _value (recursive) and the recompute loop in set_cell.
    Part 3: the while loop at the top of set_cell, and delete_cell."""

    def __init__(self):
        self.formulas = {}                           # label -> raw string: "10" or "=A1+5"
        self.values = {}                             # label -> int | None, rebuilt on every set

    def set_cell(self, cell, expression):
        if expression.startswith("="):               # part 3: walk the new formula's references; reaching cell = cycle
            stack = [t for t in expression[1:].split("+") if not t.isdigit()]
            seen = set()
            while stack:
                cur = stack.pop()
                if cur == cell:
                    return False
                if cur in seen:
                    continue
                seen.add(cur)
                raw = self.formulas.get(cur, "")
                if raw.startswith("="):
                    stack.extend(t for t in raw[1:].split("+") if not t.isdigit())
        self.formulas[cell] = expression             # part 1
        self.values = {}                             # part 2: recompute everything now, so get stays a lookup
        for c in self.formulas:
            self._value(c)
        return True

    def get_cell(self, cell):
        return self.values.get(cell)                 # one lookup

    def _value(self, cell):
        # part 2: the value of one cell; references are computed first by recursing; results land in self.values
        if cell in self.values:
            return self.values[cell]
        raw = self.formulas.get(cell)
        if raw is None:                              # unset
            v = None
        elif not raw.startswith("="):
            v = int(raw)
        else:
            v = 0
            for t in raw[1:].split("+"):
                x = int(t) if t.isdigit() else self._value(t)
                if x is None:
                    v = None
                    break
                v += x
        self.values[cell] = v
        return v

    def delete_cell(self, cell):
        self.formulas.pop(cell, None)
        self.values = {}
        for c in self.formulas:
            self._value(c)

    # the script adapter (follow-up variant), same as the cached class's
    def run_all(self, scripts):
        return [self.run_one(action) for action in scripts.split("\n")]

    def run_one(self, action):
        parts = action.split(" ")
        if parts[0] == "SET":
            return self.set_cell(parts[1], parts[2])
        elif parts[0] == "GET":
            return self.get_cell(parts[1])
        elif parts[0] == "DELETE":
            return self.delete_cell(parts[1])
        else:
            return False


# ---- the follow-up answer: same design with an explicit-stack evaluate, survives 3,000-cell chains (the 2026-10-04 solution)
class SpreadSheetCached:
    def __init__(self):
        self.cell_value_map = {}
        self.cell_formula_map = {}

    def get_cell(self, cell):
        return self.cell_value_map.get(cell, None)

    def convert_expressions(self, expression):
        # convert an expression string into list
        items = []
        if expression.startswith("="):
            #items.append("=")
            for p in expression[1:].split("+"):
                if p.isdigit():
                    items.append(int(p))
                else:
                    items.append(p)
        else:
            items = [int(expression)]
        return items

    def set_cell(self, cell, expression):
        items = self.convert_expressions(expression)     
        if self.detect_cycle(cell, items):
            return False   
        self.cell_formula_map[cell] = items
        self.recompute_all()
        return True

    def recompute_all(self):
        self.cell_value_map = {}
        for cell in self.cell_formula_map:
            self.evaluate(cell)

    def evaluate(self, start):
        # mental model: 
        # compute A1
        # A1:[B1, C1, D1, 1]
        # B1:[C2]
        # C1:[5]
        # D1:[NONE]
        stack = [start]
        while stack:
            cell = stack[-1]
            if cell in self.cell_value_map:
                stack.pop()
                continue
            if cell not in self.cell_formula_map:
                self.cell_value_map[cell] = None
                stack.pop()
                continue
            unresolved_reference = False
            for t in self.cell_formula_map[cell]:
                if isinstance(t, str) and t not in self.cell_value_map:
                    stack.append(t)
                    unresolved_reference = True
            if unresolved_reference:
                continue
            total = 0
            for t in self.cell_formula_map[cell]:
                v = t if isinstance(t, int) else self.cell_value_map[t]
                if v is None:
                    total = None
                    break
                total += v
            self.cell_value_map[cell] = total
            stack.pop()

    def detect_cycle(self, cell, items):
        stack = [t for t in items if isinstance(t, str)]
        seen = set()
        while stack:
            cur = stack.pop()
            if cur == cell:
                return True
            if cur in seen: #A1 = B1 + C1; C1 = D1 AND B1 = D1, D1 appear twice, but only need to appear once
                continue
            seen.add(cur)
            for t in self.cell_formula_map.get(cur,[]):
                if isinstance(t, str):
                    stack.append(t)            
        return False

    def del_cell(self, cell):
        self.cell_formula_map.pop(cell, None)
        self.recompute_all()        

    def run_all(self, scripts):
        res = []
        all_actions = scripts.split("\n")
        for action in all_actions:
            res.append(self.run_one(action))
        return res

    def run_one(self, action):
        # SET    -> True / False (cycle)
        # GET    -> int / None
        # DELETE -> None
        parts = action.split(" ")
        if parts[0] == "SET":
            return self.set_cell(parts[1], parts[2])
        elif parts[0] == "GET":
            return self.get_cell(parts[1])
        elif parts[0] == "DELETE":
            return self.del_cell(parts[1])
        else:
            return False

# SET Numerical value only
test_1 = "SET A1 10\nGET A1\nGET Z9"
res_1 = [True, 10, None]

# SET cell that refers to other cells
test_2 = "SET B1 =A1+5\nGET B1"
res_2 = [True, 15]

# RESET A1 = 1 and recalculate B1
test_3 = "SET A1 1\nGET B1"
res_3 = [True, 6]

# SET Empty dependency
test_4 = "SET C1 =A1+D1\nGET C1"
res_4 = [True, None]

# SET Cycle, set invalidated
test_5 = "SET A1 =B1+1\nGET B1"
res_5 = [False, 6]

# Delete, invalidate all dependency
test_6 = "DELETE A1\nGET B1"
res_6 = [None, None]

def run(scripts):            # for the test harness: the plain class
    return Spreadsheet().run_all(scripts)

if __name__ == "__main__":
    for cls in (Spreadsheet, SpreadSheetCached):
        s = cls()
        assert s.run_all(test_1) == res_1
        assert s.run_all(test_2) == res_2
        assert s.run_all(test_3) == res_3
        assert s.run_all(test_4) == res_4
        assert s.run_all(test_5) == res_5
        assert s.run_all(test_6) == res_6
    print("inline tests: both classes pass")
