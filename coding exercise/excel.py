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

Scope 2  formulas. get_cell must be O(1): compute at set time and cache the
         value of every cell, so a get is one dictionary lookup. Simplest
         correct version: on every set, recompute every cell. A cell whose
         formula depends (directly or indirectly) on an unset cell has value
         None. Setting a cell again replaces its formula and dependencies.

Scope 3  cycle detection + delete. set_cell returns False and leaves the
         sheet unchanged if the new formula would create a cycle (including
         a cell referencing itself); otherwise returns True. delete_cell
         removes a cell and returns None: its dependents now see an unset
         cell (-> None); deleting an unset cell is a no-op. Optimization: on
         set, recompute only the cells that depend on the changed cell (keep
         reverse edges).

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

class SpreadSheet:
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

def run(scripts): # for test harness
    return SpreadSheet().run_all(scripts)

if __name__ == "__main__":
    s = SpreadSheet()
        
    assert s.run_all(test_1) == res_1
    assert s.run_all(test_2) == res_2
    assert s.run_all(test_3) == res_3
    assert s.run_all(test_4) == res_4
    assert s.run_all(test_5) == res_5    
    assert s.run_all(test_6) == res_6

