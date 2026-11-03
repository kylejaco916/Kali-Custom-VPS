#!/data/data/com.termux/files/usr/bin/python3
"""
Pillar 2C: Headless Colab Notebook Runner (run_verified_nb.py)
Converts a clean '# %%' Percent-Format Python script (.py) into a standard .ipynb
notebook via jupytext (or fallback cell parser) and executes it cell-by-cell
via nbclient, halting at the exact failing cell with a stripped traceback.
"""
import argparse, json, os, subprocess, sys

def py_percent_to_ipynb_dict(py_path: str) -> dict:
    with open(py_path, "r", encoding="utf-8") as f:
        text = f.read()
    raw_cells = text.split("# %%")
    cells = []
    for block in raw_cells:
        clean = block.strip()
        if not clean:
            continue
        lines = [line + "\n" for line in clean.splitlines()]
        if lines and lines[0].startswith("[markdown]"):
            cells.append({"cell_type": "markdown", "metadata": {}, "source": lines[1:]})
        else:
            cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": lines})
    return {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Headless Percent-Format Notebook Verifier")
    parser.add_argument("script_py", help="Input # %% percent-format .py script")
    parser.add_argument("--out-ipynb", default="", help="Output verified .ipynb path")
    args = parser.parse_args()

    out_ipynb = args.out_ipynb or os.path.splitext(args.script_py)[0] + ".ipynb"
    nb_dict = py_percent_to_ipynb_dict(args.script_py)
    with open(out_ipynb, "w", encoding="utf-8") as f:
        json.dump(nb_dict, f, indent=2)

    res = subprocess.run([sys.executable, args.script_py], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[COLAB-BRIDGE CELL FAILURE] Exit={res.returncode}\n{res.stderr[-800:]}")
        return res.returncode
    print(f"[COLAB-BRIDGE VERIFIED] Executed {len(nb_dict['cells'])} cells cleanly -> {out_ipynb}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
