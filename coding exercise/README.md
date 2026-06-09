# 🚀 LeetCode Coding Exercise Environment

Welcome to your local LeetCode playground! This environment is pre-configured for **Python 3** and **C++ (C++20)** development.

---

## 📂 Folder Structure

```text
coding exercise/
├── README.md          # This instruction guide
├── runner.py          # CLI runner for quick execution and compilation
├── template.py        # Python LeetCode starter template
└── template.cpp       # C++ LeetCode starter template
```

---

## ⚡ Quick Start with CLI Runner

The custom `runner.py` handles the execution of Python files and compiles/runs C++ files automatically with colored logs.

### 🐍 Running Python Solutions
```bash
./runner.py template.py
# or
python3 runner.py template.py
```

### 🦀 Running C++ Solutions
The runner automatically invokes `clang++` with standard debugging symbols and C++20 library support, creates a binary `filename.out` (which is git-ignored), executes it, and displays execution status.
```bash
./runner.py template.cpp
# or
python3 runner.py template.cpp
```

---

## 🛠️ VS Code Integration (Run & Debug)

We have configured `.vscode/tasks.json` and `.vscode/launch.json` in the workspace root. You can debug directly inside VS Code!

### How to Debug / Run:
1. Open the file you want to work on (e.g., `template.py` or `template.cpp`).
2. Press `F5` or click **Run -> Start Debugging** in VS Code.
3. **C++**: VS Code will automatically compile the active file into `<filename>.out` using the configured task and run the LLDB debugger. You can set breakpoints and inspect structures.
4. **Python**: VS Code will run the Python debugger (`debugpy`) on the current file directly.

---

## 💡 LeetCode Helpers Built into Templates

Both `template.py` and `template.cpp` have built-in utilities to make testing structures like **Linked Lists** and **Binary Trees** extremely easy.

### 🔗 Linked Lists
Instead of manually building linked lists node-by-node:
* **Python**: Use `list_to_linked_list([1, 2, 3])` to build a chain of `ListNode`. Convert it back using `linked_list_to_list(head)`.
* **C++**: Use `listToLinkedList({1, 2, 3})`. Clean up memory afterwards with `freeLinkedList(head)`.

### 🌳 Binary Trees
Supports LeetCode's level-order array representation (which includes `null`/`None` for empty nodes):
* **Python**: `list_to_binary_tree([1, None, 2, 3])`
* **C++**: `listToBinaryTree({"1", "null", "2", "3"})`
* **Visualization**: Both templates contain a `print_tree` / `printTree` helper that prints a clean, rotated hierarchical tree structure directly in the terminal, like:
  ```text
  │   ┌── 2
  │   │   └── 3
  └── 1
  ```
