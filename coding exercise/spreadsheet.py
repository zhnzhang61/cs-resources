#!/usr/bin/env python3
"""
Spreadsheet Formula Evaluator

The input is a multi-line command script; return one result string per command.

SET label value
    label: uppercase letters followed by digits (A1, B10, AA1).
    value: a non-negative integer, or an addition-only formula of integers
           and/or labels (A1+A2+5).
    If the assignment would create a dependency cycle, return "ERROR" and
    leave the sheet unchanged. Otherwise return "OK".

GET label
    Return the evaluated value as a string. Return "ERROR" if the cell is
    unset, or if anything it depends on (directly or indirectly) is unset.

Lazy or eager evaluation is your choice; GET must always reflect the latest
committed values.

Parts:
    1. literals: SET / GET / parsing
    2. formulas that reference other cells
    3. cycle detection with rollback
    4. bonus: a 3000-cell chain

Run the tests:  python3 test_spreadsheet.py        (all parts)
                python3 test_spreadsheet.py 2      (part 2 only)
or just run this file (F5 in VS Code).
"""


def run(script: str) -> list[str]:
    cells = {}
    result = []
    def get_cell_value(cell):
        value = calculate_value(cell)
        if value is None:
            return "ERROR"
        else:
            return str(value)
        

    def calculate_value(cell):
        # Find, evaluate and update dependencies for each cell in the expression without using recursion
        # Assume there will be no cycle in the expression
        # Return the value of the expression
        memo = {}
        stack = [cell]
        while stack:
            current = stack[-1]
            if current in memo:
                stack.pop()
                continue
            if current not in cells:
                return None
            missing = [item for item in cells[current] if isinstance(item, str) and item not in memo]
            if missing:
                stack.extend(missing)
            else:
                memo[current] = sum(memo[item] if isinstance(item, str) else item for item in cells[current])
                stack.pop()            
        return memo[cell]

    def set_cell_value(cell, value):
        # set method should detect cycle and return "ERROR" if it exists
        # set the value of the cell first, then detect cycle
        # cell looks like A1, A2, A3, etc.
        # value looks like A1+1, its a mixture of cells, + operator and integers
        items = []
        for item in value.split("+"):
            if item.isdigit():
                items.append(int(item))
            else:
                items.append(item)

        # we want to
        # save the previous value    
        if cell in cells:
            previous = cells[cell]
            has_previous = True
        else:
            previous = None
            has_previous = False

        # set new value first, detect cycle next 
        cells[cell] = items
        retval = detect_cycle(cell)

        #then roll back to previous value if there is a cycle    
        if retval == "ERROR":
            if has_previous:
                cells[cell] = previous
            else:
                del cells[cell]
        return retval

    def detect_cycle(cell):
        # detect cycle and return "ERROR" if it exists
        # return "OK" if there is no cycle
        stack = []
        for item in cells[cell]:
            if isinstance(item, str):
                stack.append(item)

        visited = set() 
        while stack:
            current = stack.pop()
            if current == cell: 
                return "ERROR"
            if current in visited:
                continue
            visited.add(current)
            if current in cells:
                for item in cells[current]:
                    if isinstance(item, str):
                        stack.append(item)
        return "OK"

    for line in script.split("\n"):
        parts = line.split(" ")
        if parts[0] == "SET":            
            action, cell, value = parts
            result.append(set_cell_value(cell, value))
        elif parts[0] == "GET":
            action, cell = parts
            result.append(get_cell_value(cell))
        else:
            raise ValueError(f"Invalid line: {line}")
    return result

if __name__ == "__main__":
    from test_spreadsheet import main
    main()
