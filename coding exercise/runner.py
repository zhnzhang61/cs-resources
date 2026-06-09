#!/usr/bin/env python3
import sys
import os
import subprocess

# ANSI Colors for beautiful UI
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner(text, color=BLUE):
    print(f"\n{color}{BOLD}{'=' * 50}{RESET}")
    print(f"{color}{BOLD}  {text}{RESET}")
    print(f"{color}{BOLD}{'=' * 50}{RESET}")

def run_python(filepath):
    print(f"{BLUE}[Runner] Executing Python script: {os.path.basename(filepath)}...{RESET}\n")
    try:
        result = subprocess.run([sys.executable, filepath], check=True)
        print(f"\n{GREEN}{BOLD}[Success] Execution finished with exit code {result.returncode}.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"\n{RED}{BOLD}[Error] Execution failed with exit code {e.returncode}.{RESET}")

def run_cpp(filepath):
    file_dir = os.path.dirname(filepath)
    file_name = os.path.basename(filepath)
    base_name = os.path.splitext(file_name)[0]
    output_bin = os.path.join(file_dir if file_dir else ".", f"{base_name}.out")
    
    print(f"{BLUE}[Runner] Compiling C++ file: {file_name}...{RESET}")
    # Compile with clang++ std=c++20
    compile_cmd = [
        "clang++",
        "-std=c++20",
        "-stdlib=libc++",
        "-g",
        filepath,
        "-o",
        output_bin
    ]
    
    try:
        subprocess.run(compile_cmd, check=True)
        print(f"{GREEN}[Success] Compilation succeeded! Created {os.path.basename(output_bin)}{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"\n{RED}{BOLD}[Error] Compilation failed.{RESET}")
        return

    print(f"{BLUE}[Runner] Executing binary...{RESET}\n")
    try:
        result = subprocess.run([output_bin], check=True)
        print(f"\n{GREEN}{BOLD}[Success] Program finished with exit code {result.returncode}.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"\n{RED}{BOLD}[Error] Execution failed with exit code {e.returncode}.{RESET}")

def main():
    if len(sys.argv) < 2:
        print(f"{YELLOW}Usage: python3 runner.py <filename.py | filename.cpp>{RESET}")
        print(f"Example: {GREEN}python3 runner.py template.py{RESET}")
        sys.exit(1)
        
    target = sys.argv[1]
    if not os.path.exists(target):
        # Check if the target is in the same directory as the runner
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alternative = os.path.join(script_dir, target)
        if os.path.exists(alternative):
            target = alternative
        else:
            print(f"{RED}[Error] File not found: {sys.argv[1]}{RESET}")
            sys.exit(1)

    _, ext = os.path.splitext(target.lower())
    if ext == ".py":
        run_python(target)
    elif ext in [".cpp", ".cc", ".cxx"]:
        run_cpp(target)
    else:
        print(f"{RED}[Error] Unsupported file extension '{ext}'. Only Python (.py) and C++ (.cpp) are supported.{RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()
