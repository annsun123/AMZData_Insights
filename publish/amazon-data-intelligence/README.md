# Amazon Data Intelligence

**Personal knowledge base & portfolio — data-driven Amazon market analysis.**

Using Python, statistics, and real scraped data to understand how the Amazon marketplace actually works. This is where I document my analysis methodology, findings, and code.

---

## Analyses

| # | Analysis | Date | Key Finding |
|---|----------|------|-------------|
| 001 | [**The Review Moat**](analyses/001-review-moat/) — Quantifying the review barrier across Amazon categories | Jun 2026 | Reviews don't predict rank in 3/10 categories; Amazon has a "Two-Tier" competitive structure |

---

## Why I Built This

Amazon sellers are drowning in data but starving for insight. Existing tools show dashboards — they don't answer causal questions. I wanted to:

- Apply real statistical methods to e-commerce problems
- Build reproducible data pipelines (scraping → analysis → visualization)
- Develop the skill of finding "surprising" signals in noisy marketplace data
- Have a body of work that demonstrates data science thinking end-to-end

---

## My Process

Each analysis follows the same pipeline:

```
Research → Methodology Design → Data Pipeline → Statistical Analysis → Quality Review → Write-up
```

| Phase | What happens |
|-------|-------------|
| **Research** | Identify a question sellers actually care about. Search Reddit/LinkedIn to confirm demand. |
| **Methodology** | Design the statistical approach. What tests? What hypotheses? What data do I need? |
| **Data Pipeline** | Build scrapers. Collect and clean real Amazon data. |
| **Analysis** | EDA → statistical tests → visualization → find the surprises. |
| **Review** | Verify every data claim. Audit the statistics. Score the narrative. |
| **Write-up** | Notebook + charts + plain-English summary. The analysis has to work for both data scientists and sellers. |

---

## Tech Stack

```
Python · pandas · scipy · statsmodels · scikit-learn · matplotlib · seaborn
Jupyter · BeautifulSoup (scraping) · Plotly (interactive viz)
```

---

## Repo Structure

```
amazon-data-intelligence/
├── README.md
├── analyses/
│   └── 001-review-moat/
│       ├── README.md            ← Start here for each analysis
│       ├── notebook.ipynb       ← Full reproducible notebook
│       ├── dashboard.html       ← Interactive summary
│       └── charts/              ← Publication-quality PNGs
├── data/                        ← Cleaned datasets
└── methodology/                 ← Reusable methodology templates
```

---

## About Me

Data professional building hands-on expertise in marketplace analytics, statistical modeling, and data storytelling. This repo is my learning in public — every analysis represents something I figured out along the way.

---

*Started June 2026. Updated as I learn.*
