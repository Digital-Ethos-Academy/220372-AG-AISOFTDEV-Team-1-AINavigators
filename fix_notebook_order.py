#!/usr/bin/env python3
"""
Fix the cell ordering in Capstone_Phase5_Frontend.ipynb
"""
import json
import shutil
from pathlib import Path

NOTEBOOK_PATH = Path("Python Notebooks/Capstone_Phase5_Frontend.ipynb")
BACKUP_PATH = Path("Python Notebooks/Capstone_Phase5_Frontend_BACKUP.ipynb")

# Backup the original
shutil.copy(NOTEBOOK_PATH, BACKUP_PATH)
print(f"✅ Backed up original to: {BACKUP_PATH}")

# Load notebook
with open(NOTEBOOK_PATH) as f:
    nb = json.load(f)

# Cell IDs in the CORRECT order (determined by analyzing the content)
correct_order = [
    # Keep original Dashboard cells (these are correct)
    '79752c53',  # Model and Config Setup (markdown)
    'f5d3b2fc',  # import setup
    '5f9b114f',  # Get the Desired UI Screenshot (markdown)
    '1e7ad305',  # VIEW 1: Dashboard - Generate Image
    '72d760c0',  # Generate Monolithic UI Code (markdown)
    'a1d9766c',  # Explain Dashboard Image
    '2d0b4502',  # Now, generate the monolithic... (markdown)
    '90325e48',  # Generate Dashboard Monolithic
    'f795aa13',  # Refactor in Reusable Components (markdown)
    'f9eeca29',  # Refactor Dashboard

    # Templates (keep as reference)
    '5ijh82yuzkl',  # Additional Views Templates (markdown)
    '7lnfb13uxlx',  # Template code cell

    # VIEW 2: Projects (correct order)
    '287g15iydbd',  # VIEW 2: Projects Management (markdown)
    'kvtudtnmt9',  # Generate Projects Image
    'zr0lr7sjba',  # Explain Projects Image
    's2xzst1v5g',  # Generate Projects Monolithic
    'jf41p6v6p1',  # Refactor Projects

    # VIEW 3: Allocations (correct order)
    'bg8qe81v7tn',  # VIEW 3: Allocations Calendar (markdown)
    '9uwhny07yy',  # Generate Allocations Image
    'l3i32xpsfs',  # Explain Allocations Image
    'r24lzjpnr7m',  # Generate Allocations Monolithic
    'ygn59v32ua',  # Refactor Allocations

    # VIEW 4: Employees (correct order)
    'jbj3ya3z2xq',  # VIEW 4: Employees Management (markdown)
    'ju7g5mrzx3',  # Generate Employees Image
    '2gj7xbvozl7',  # Explain Employees Image
    'ucx1gjj46z',  # Generate Employees Monolithic
    'cnmeva6k2dk',  # Refactor Employees

    # VIEW 5: AI Recommendations (correct order)
    'nz3fezpzvr',  # VIEW 5: AI Recommendations (markdown)
    'dfrqmobmpc8',  # Generate AI Recommendations Image
    'i9tat1kxzo9',  # Explain AI Recommendations Image
    'c3clsng7jzl',  # Generate AI Recommendations Monolithic
    'c9o61w5jzm9',  # Refactor AI Recommendations

    # Summary
    '75rogjjunaf',  # Summary (markdown)
]

# Create a mapping of cell_id to cell
cell_map = {cell['id']: cell for cell in nb['cells']}

# Reorder cells
new_cells = []
for cell_id in correct_order:
    if cell_id in cell_map:
        new_cells.append(cell_map[cell_id])
    else:
        print(f"⚠️  Warning: Cell {cell_id} not found")

# Add any remaining cells that weren't in our list (just in case)
included_ids = set(correct_order)
for cell in nb['cells']:
    if cell['id'] not in included_ids:
        print(f"⚠️  Adding unlisted cell: {cell['id']}")
        new_cells.append(cell)

# Update notebook
nb['cells'] = new_cells

# Save corrected notebook
with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"✅ Fixed notebook saved to: {NOTEBOOK_PATH}")
print(f"   Total cells: {len(new_cells)}")
print(f"\n📝 To restore the backup if needed:")
print(f"   mv '{BACKUP_PATH}' '{NOTEBOOK_PATH}'")