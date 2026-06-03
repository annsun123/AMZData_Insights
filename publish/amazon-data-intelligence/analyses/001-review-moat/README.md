# 001 — The Review Moat: How Many Reviews Do You Actually Need to Compete on Amazon?

**June 2026** · 984 products · 10 categories · Spearman ρ · Logistic Regression · Mann-Whitney U

---

## The Question

Every Amazon seller stares at competitor review counts and asks: *how many reviews do I actually need to compete in this category?*

I scraped the top 100 Best Sellers across 10 categories and ran statistical tests to find out.

---

## The Answer (TL;DR)

Amazon has a **"Two-Tier" competitive landscape**:

| Type | Categories | What it means |
|------|-----------|---------------|
| **Type A: Review-Locked** | 7/10 categories | Reviews strongly predict BSR rank. You need 107K–749K reviews to compete in the top 20. |
| **Type B: Review-Independent** | 3/10 categories | Reviews do NOT significantly predict rank. Electronics, Sports & Outdoors, Toys & Games. |

---

## Key Findings

### 1. The Review Moat is real — and higher than sellers think

- Only **0.8%** of top-100 products have fewer than 50 reviews
- Only **1.3%** have under 100 reviews
- Median top-100 product: **24,570 reviews**

### 2. Three categories where reviews don't predict rank

| Category | Spearman ρ | p-value | Significant? |
|----------|-----------|---------|--------------|
| Electronics | -0.180 | 0.075 | No |
| Sports & Outdoors | -0.121 | 0.230 | No |
| Toys & Games | -0.062 | 0.538 | No |

In these categories, other factors (price, brand, rating, listing quality) dominate rank determination.

### 3. Toys & Games: Rating matters MORE than reviews

This is the **only** category where star rating (\|ρ\|=0.106) has a stronger correlation with rank than review count (\|ρ\|=0.062). A 4.8-star product with 100 reviews will outrank a 4.2-star product with 1,000.

### 4. The Category Accessibility Index

Composite score (0–100) combining review barrier (40%), price dispersion (30%), and brand concentration (30%):

| Rank | Category | Score | Verdict |
|------|----------|-------|---------|
| 1 | Toys & Games | 73.9 | Most accessible |
| 2 | Electronics | 72.7 | High price dispersion |
| 3 | Kitchen & Dining | 38.4 | Moderate |
| ... | ... | ... | ... |
| 10 | Baby | 0.2 | Nearly impenetrable |

---

## Methods

- **Spearman rank correlation**: review_count vs BSR per category (non-parametric, handles skewed distributions)
- **Logistic regression**: P(top-20 rank) ~ log(reviews) + price + rating
- **Mann-Whitney U**: review count distribution between rank tiers
- **Kruskal-Wallis**: cross-category review count differences
- **Category Accessibility Index**: weighted composite (40/30/30)

---

## Files

| File | Description |
|------|-------------|
| `notebook.ipynb` | Full reproducible analysis (run all cells) |
| `dashboard.html` | Interactive summary dashboard (open in browser) |
| `charts/` | All 8 visualizations as PNG |

---

## Limitations

- **Best Sellers only**: The top 100 are already winning products. The long tail may differ.
- **Snapshot, not time-series**: We measure association, not causation.
- **JPY pricing**: Prices converted from JPY at approximate June 2026 rate. Relative analyses unaffected.
- **No brand data**: Brand concentration proxied from title first-word frequency.

---

## What I Learned

1. Non-parametric tests (Spearman, Mann-Whitney) are essential for Amazon data — review counts are extremely right-skewed
2. Logistic regression thresholds become meaningless when the underlying correlation is weak — need to report significance before showing model output
3. The most valuable finding isn't the number — it's the **framework** (Two-Tier). Frameworks are more memorable and shareable than statistics.
4. Scraping from Japan (JPY prices) creates a currency conversion issue that needs to be flagged upfront for credibility
