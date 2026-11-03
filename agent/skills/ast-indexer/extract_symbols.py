#!/data/data/com.termux/files/usr/bin/python3
"""
Lightweight Termux ARM64 AST & Regex Symbol Indexer
Extracts classes, functions, signatures, and imports without loading entire files into context.
"""
import sys, os, ast

def index_python_file(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read(), filename=filepath)
        print(f"=== AST SYMBOLS: {filepath} ===")
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                print(f"  [DEF] {node.name}({', '.join(args)}) @ L{node.lineno}")
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                print(f"  [CLASS] {node.name} @ L{node.lineno} -> methods: {methods}")
    except Exception as e:
        print(f"  [AST-ERR] {filepath}: {e}")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        if os.path.isfile(p) and p.endswith(".py"):
            index_python_file(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for file in files:
                    if file.endswith(".py"):
                        index_python_file(os.path.join(root, file))
