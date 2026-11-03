---
name: colab-bridge
description: Headless notebook execution bridge. Writes '# %%' percent-format Python scripts, converts them to .ipynb, and verifies cell-by-cell execution before exporting notebooks.
---
# Headless Colab Execution Bridge
Never write raw `.ipynb` JSON by hand. Write clean Python scripts segmented with `# %%` cell markers and verify + compile them deterministically via:
`python3 ~/.gemini/antigravity/skills/colab-bridge/scripts/run_verified_nb.py <pipeline.py> --out-ipynb <verified.ipynb>`
