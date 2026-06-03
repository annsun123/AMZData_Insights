"""Convert run_analysis.py to a Jupyter notebook"""
import json, os, re

with open('run_analysis.py', 'r', encoding='utf-8') as f:
    source = f.read()

nb = {
    'nbformat': 4,
    'nbformat_minor': 5,
    'metadata': {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.11.0'}
    },
    'cells': []
}

# Markdown header
nb['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '# Review Moat Analysis - AMZ Data Intelligence\n',
        '**Date**: 2026-06-02  \n',
        '**Analyst**: Data Storyteller  \n',
        '**Data**: 984 products across 10 Amazon categories\n',
        '\n',
        'This notebook reproduces the complete analysis: EDA, statistical tests, visualizations, and the Category Accessibility Index.'
    ]
})

# Split into cells at major section boundaries
lines = source.split('\n')
cells_lines = []
current = []

for line in lines:
    if any(line.startswith(prefix) for prefix in [
        'print(\"=\" * 70)',
        '# ── Load',
        '# ── EDA',
        '# ── STATISTICAL',
        '# ── Cross-category',
        '# ── Category Accessibility',
        '# ── VISUALIZATIONS',
        'print(\"\\n\" + \"=\" * 70)',
        '# --- Chart 1:',
        '# --- Chart 2:',
        '# --- Chart 3:',
        '# --- Chart 4:',
        '# --- Chart 5:',
        '# --- Chart 6:',
        '# --- Chart 7:',
        '# --- Chart 8:',
        '# ── SURPRISE FINDINGS',
    ]):
        if current:
            cells_lines.append(current)
            current = []
        current.append(line)
    else:
        current.append(line)

if current:
    cells_lines.append(current)

for cell_lines in cells_lines:
    nb['cells'].append({
        'cell_type': 'code',
        'metadata': {},
        'source': [l + '\n' for l in cell_lines],
        'outputs': [],
        'execution_count': None
    })

# Final markdown
nb['cells'].append({
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '## Conclusions\n',
        '\n',
        'See `../tasks/active/review-moat-analysis/analysis.md` for the full written analysis with content drafts.\n',
        '\n',
        '### Key Takeaways\n',
        '- The Review Moat is real: only 0.8% of top-100 products have less than 50 reviews\n',
        '- But 3/10 categories are Review-Independent (Electronics, Sports and Outdoors, Toys and Games)\n',
        '- Toys and Games is the most accessible category (Index = 73.9/100)\n',
        '- In Toys and Games, rating matters MORE than review count for predicting rank\n',
        '- Baby is the most impenetrable category (Index = 0.2/100)\n'
    ]
})

os.makedirs('notebooks', exist_ok=True)
with open('notebooks/review_moat_analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('[OK] Notebook saved to notebooks/review_moat_analysis.ipynb')
print(f'Total cells: {len(nb["cells"])}')
