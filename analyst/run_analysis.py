"""
Review Moat Analysis — Phase B: Data Science Execution
Data Storyteller, AMZ Data Intelligence
Date: 2026-06-02
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from scipy.stats import spearmanr, mannwhitneyu, kruskal
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings, os, sys
warnings.filterwarnings('ignore')

# ── Setup ──────────────────────────────────────────────
DATA_PATH = "../data/raw/2026-06-01_amazon_best_sellers_review-moat.csv"
VIZ_DIR  = "../data/visualizations/review-moat-analysis"
DATE     = "2026-06-02"
os.makedirs(VIZ_DIR, exist_ok=True)

# Color palette (colorblind-friendly via seaborn 'colorblind')
sns.set_theme(style="whitegrid", palette="colorblind", font="sans-serif")
CB_PALETTE = sns.color_palette("colorblind", 10)
plt.rcParams.update({'figure.dpi': 150, 'savefig.dpi': 150, 'savefig.bbox': 'tight'})

# ── Load & Clean ───────────────────────────────────────
print("=" * 70)
print("1. LOADING DATA")
print("=" * 70)

df = pd.read_csv(DATA_PATH)
print(f"Raw shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Deduplicate by ASIN (keep lowest BSR rank = best rank)
df = df.sort_values('bsr_rank').drop_duplicates(subset='asin', keep='first').reset_index(drop=True)

# Convert price from JPY to USD (approximate: 1 JPY ≈ 0.0069 USD as of mid-2026)
JPY_TO_USD = 0.0069
df['price_usd'] = df['price'] * JPY_TO_USD

# Create derived columns
df['log_reviews'] = np.log1p(df['review_count'])
df['in_top20'] = (df['bsr_rank'] <= 20).astype(int)
df['rank_tier'] = pd.cut(df['bsr_rank'], bins=[0, 20, 50, 100], labels=['Top 20', '21-50', '51-100'])
df['price_usd'] = df['price_usd'].fillna(df.groupby('category')['price_usd'].transform('median'))
df['rating'] = df['rating'].fillna(df.groupby('category')['rating'].transform('median'))

print(f"After dedup: {df.shape[0]} rows")
print(f"Categories: {df['category'].nunique()}")
print(f"Missing after fill — price_usd: {df['price_usd'].isna().sum()}, rating: {df['rating'].isna().sum()}")

# ── EDA ────────────────────────────────────────────────
print("\n" + "=" * 70)
print("2. EXPLORATORY DATA ANALYSIS")
print("=" * 70)

print("\n── Per-Category Summary ──")
cat_summary = df.groupby('category').agg(
    n_products=('asin', 'count'),
    median_bsr=('bsr_rank', 'median'),
    mean_reviews=('review_count', 'mean'),
    median_reviews=('review_count', 'median'),
    mean_rating=('rating', 'mean'),
    mean_price_usd=('price_usd', 'mean'),
    median_price_usd=('price_usd', 'median'),
    pct_top20_low_reviews=('in_top20', lambda x: (df.loc[x.index, 'review_count'] <= 50).sum() / len(x) * 100),
    products_under_50_reviews=('review_count', lambda x: (x <= 50).sum()),
    products_under_100_reviews=('review_count', lambda x: (x <= 100).sum()),
    products_under_500_reviews=('review_count', lambda x: (x <= 500).sum()),
).round(2)

cat_summary['pct_under_50'] = (cat_summary['products_under_50_reviews'] / cat_summary['n_products'] * 100).round(1)
cat_summary['pct_under_100'] = (cat_summary['products_under_100_reviews'] / cat_summary['n_products'] * 100).round(1)
cat_summary['pct_under_500'] = (cat_summary['products_under_500_reviews'] / cat_summary['n_products'] * 100).round(1)
print(cat_summary.to_string())

print("\n── Review Count Distribution ──")
print(df['review_count'].describe())
print(f"\n% with < 50 reviews: {(df['review_count'] < 50).mean()*100:.1f}%")
print(f"% with < 100 reviews: {(df['review_count'] < 100).mean()*100:.1f}%")
print(f"% with < 500 reviews: {(df['review_count'] < 500).mean()*100:.1f}%")
print(f"Max reviews: {df['review_count'].max():,}")

print("\n── Review Count Distribution ──")
print(df['review_count'].describe())
print(f"\n% with < 50 reviews: {(df['review_count'] < 50).mean()*100:.1f}%")
print(f"% with < 100 reviews: {(df['review_count'] < 100).mean()*100:.1f}%")
print(f"% with < 500 reviews: {(df['review_count'] < 500).mean()*100:.1f}%")
print(f"Max reviews: {df['review_count'].max():,}")

print("\n── Rank Tier Distribution ──")
print(df['rank_tier'].value_counts())
print(f"\nTop 20 breakdown:")
print(df[df['in_top20'] == 1].groupby('category').size())

# ── STATISTICAL TESTS ──────────────────────────────────
print("\n" + "=" * 70)
print("3. STATISTICAL TESTS")
print("=" * 70)

results = {}  # store per-category results

for cat in sorted(df['category'].unique()):
    cat_df = df[df['category'] == cat]
    print(f"\n── {cat} (n={len(cat_df)}) ──")

    # Spearman rank correlation
    rho, p_spearman = spearmanr(cat_df['review_count'], cat_df['bsr_rank'])
    print(f"  Spearman ρ(reviews, BSR): {rho:.3f}, p={p_spearman:.4f} {'***' if p_spearman < 0.001 else '**' if p_spearman < 0.01 else '*' if p_spearman < 0.05 else 'ns'}")

    # Logistic regression: P(top-20) ~ log(reviews) + price + rating
    X = cat_df[['log_reviews', 'price_usd', 'rating']].values
    y = cat_df['in_top20'].values
    lr = LogisticRegression(max_iter=1000)
    try:
        lr.fit(X, y)
        # Review count at which P(top-20) = 0.5
        # logit(p) = b0 + b1*log_reviews + b2*price + b3*rating
        # log_reviews_for_p50 = -(b0 + b2*median_price + b3*median_rating) / b1
        b0, b1, b2, b3 = lr.intercept_[0], lr.coef_[0][0], lr.coef_[0][1], lr.coef_[0][2]
        median_price = cat_df['price_usd'].median()
        median_rating = cat_df['rating'].median()
        log_rev_threshold = -(b0 + b2*median_price + b3*median_rating) / b1
        review_threshold = np.exp(log_rev_threshold) - 1  # reverse log1p
        review_threshold = max(0, review_threshold)
        print(f"  Logistic: P(top-20)=0.5 at ~{review_threshold:.0f} reviews (log_reviews coef={b1:.3f})")
    except Exception as e:
        b1, review_threshold = np.nan, np.nan
        print(f"  Logistic regression failed: {e}")

    # Probability by review bucket
    bins = [0, 10, 25, 50, 100, 250, 500, 1000, float('inf')]
    labels = ['0-10', '11-25', '26-50', '51-100', '101-250', '251-500', '501-1000', '1000+']
    cat_df['review_bucket'] = pd.cut(cat_df['review_count'], bins=bins, labels=labels)
    bucket_prob = cat_df.groupby('review_bucket', observed=False)['in_top20'].agg(['mean', 'count'])

    results[cat] = {
        'n': len(cat_df),
        'spearman_rho': rho,
        'spearman_p': p_spearman,
        'review_threshold': review_threshold,
        'log_reviews_coef': b1,
        'median_reviews': cat_df['review_count'].median(),
        'pct_under_50': (cat_df['review_count'] <= 50).mean() * 100,
        'pct_under_100': (cat_df['review_count'] <= 100).mean() * 100,
        'median_price_usd': cat_df['price_usd'].median(),
        'price_cv': cat_df['price_usd'].std() / cat_df['price_usd'].mean() if cat_df['price_usd'].mean() > 0 else 0,
        'bucket_probs': bucket_prob,
    }

# ── Cross-category tests ──
print("\n── Cross-Category Tests ──")
# Kruskal-Wallis: does review_count differ across categories?
kw_stat, kw_p = kruskal(*[df[df['category']==c]['review_count'].values for c in sorted(df['category'].unique())])
print(f"Kruskal-Wallis H: {kw_stat:.1f}, p={kw_p:.2e} — categories {'DO' if kw_p < 0.05 else 'do NOT'} differ significantly")

# Mann-Whitney U for rank tiers
top20 = df[df['in_top20']==1]['review_count']
rest = df[df['in_top20']==0]['review_count']
mw_stat, mw_p = mannwhitneyu(top20, rest, alternative='two-sided')
print(f"Mann-Whitney U (top20 vs rest): U={mw_stat:,.0f}, p={mw_p:.2e}")

# Rating vs Reviews comparison per category
print("\n── Standardized Coefficients: Rating vs log(Reviews) predicting BSR ──")
for cat in sorted(df['category'].unique()):
    cat_df = df[df['category'] == cat].copy()
    scaler = StandardScaler()
    X = scaler.fit_transform(cat_df[['log_reviews', 'rating']])
    y = -cat_df['bsr_rank'].values  # negate so higher = better rank
    # Simple OLS-ish: correlation comparison
    r_reviews = spearmanr(cat_df['log_reviews'], cat_df['bsr_rank'])[0]
    r_rating = spearmanr(cat_df['rating'], cat_df['bsr_rank'])[0]
    stronger = "Reviews" if abs(r_reviews) > abs(r_rating) else "Rating"
    print(f"  {cat:<30s}: ρ_reviews={r_reviews:+.3f}  ρ_rating={r_rating:+.3f}  → {stronger} matters more")

# ── Category Accessibility Index ──
print("\n── Category Accessibility Index ──")
# Component 1: Review barrier (% of top-100 with ≤50 reviews) — higher = better
# Component 2: Price dispersion (CV) — higher = more room to differentiate
# Component 3: Concentration (share of top 20 held by top 3 brands — proxy with title keyword concentration)
# For concentration: % of top 20 products whose title starts with same first word as top 3 brands
def calc_concentration(cat_df):
    """Approximate brand concentration: share of top 20 held by 3 most common title-start words."""
    top20_titles = cat_df[cat_df['in_top20'] == 1]['title']
    first_words = top20_titles.str.split().str[0].value_counts()
    top3_share = first_words.head(3).sum() / len(top20_titles) if len(top20_titles) > 0 else 0.5
    return top3_share

accessibility = []
for cat in sorted(df['category'].unique()):
    cat_df = df[df['category'] == cat]
    pct_under_50 = (cat_df['review_count'] <= 50).mean() * 100
    price_cv = cat_df['price_usd'].std() / cat_df['price_usd'].mean() if cat_df['price_usd'].mean() > 0 else 0
    concentration = calc_concentration(cat_df)
    accessibility.append({
        'category': cat,
        'pct_under_50_reviews': pct_under_50,
        'price_cv': price_cv,
        'brand_concentration_top3': concentration,
    })

acc_df = pd.DataFrame(accessibility)

# Min-max normalize each component to 0-100
for col in ['pct_under_50_reviews', 'price_cv', 'brand_concentration_top3']:
    min_v, max_v = acc_df[col].min(), acc_df[col].max()
    if max_v - min_v > 0:
        acc_df[f'{col}_norm'] = (acc_df[col] - min_v) / (max_v - min_v) * 100
    else:
        acc_df[f'{col}_norm'] = 50

# For brand_concentration: LOWER concentration = BETTER (invert)
acc_df['brand_concentration_top3_norm'] = 100 - acc_df['brand_concentration_top3_norm']

# Weighted composite
acc_df['accessibility_index'] = (
    0.40 * acc_df['pct_under_50_reviews_norm'] +
    0.30 * acc_df['price_cv_norm'] +
    0.30 * acc_df['brand_concentration_top3_norm']
)

acc_df = acc_df.sort_values('accessibility_index', ascending=False)
print(acc_df[['category', 'pct_under_50_reviews', 'price_cv', 'accessibility_index']].to_string(index=False))

print("\n[OK] Statistical analysis complete. Generating visualizations...")

# ── VISUALIZATIONS ─────────────────────────────────────
print("\n" + "=" * 70)
print("4. CREATING VISUALIZATIONS")
print("=" * 70)

# --- Chart 1: Review Count vs BSR Rank (facet grid) ---
print("  Chart 1: Review vs BSR Facet Grid")
fig, axes = plt.subplots(2, 5, figsize=(20, 9), sharex=False, sharey=True)
axes = axes.flatten()
for i, (cat, ax) in enumerate(zip(sorted(df['category'].unique()), axes)):
    cat_df = df[df['category'] == cat]
    ax.scatter(cat_df['review_count'], cat_df['bsr_rank'], alpha=0.5, s=20, c=[CB_PALETTE[i]])
    # LOESS-like: simple rolling mean
    sorted_df = cat_df.sort_values('review_count')
    from scipy.interpolate import make_interp_spline
    try:
        x_sorted = sorted_df['review_count'].values
        y_sorted = sorted_df['bsr_rank'].values
        # Use lowess from statsmodels if available, else simple poly
        from statsmodels.nonparametric.smoothers_lowess import lowess
        lowess_result = lowess(y_sorted, x_sorted, frac=0.4, return_sorted=True)
        ax.plot(lowess_result[:, 0], lowess_result[:, 1], 'k-', linewidth=1.5, alpha=0.8)
    except Exception:
        pass
    ax.set_title(cat.replace(' & ', '\n& '), fontsize=9, fontweight='bold')
    ax.set_xlabel('Reviews' if i >= 5 else '')
    ax.set_ylabel('BSR Rank' if i in [0, 5] else '')
    ax.invert_yaxis()
    ax.set_xlim(left=-50)
fig.suptitle('Review Count vs BSR Rank by Category\n(Lower rank = better. Black curve = LOESS trend)', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart1_review_vs_bsr_facet.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

# --- Chart 2: Review Distribution by Rank Tier (Box Plot) ---
print("  Chart 2: Review Distribution by Rank Tier")
fig, axes = plt.subplots(2, 5, figsize=(20, 9))
axes = axes.flatten()
for i, (cat, ax) in enumerate(zip(sorted(df['category'].unique()), axes)):
    cat_df = df[df['category'] == cat]
    # Filter: only show up to 99th percentile to avoid extreme outliers
    cutoff = cat_df['review_count'].quantile(0.95)
    plot_df = cat_df[cat_df['review_count'] <= cutoff]
    bp = plot_df.boxplot(column='review_count', by='rank_tier', ax=ax, patch_artist=True,
                         boxprops=dict(facecolor=CB_PALETTE[i], alpha=0.6))
    ax.set_title(cat.replace(' & ', '\n& '), fontsize=9, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('Reviews' if i in [0, 5] else '')
    ax.tick_params(axis='x', rotation=30, labelsize=7)
fig.suptitle('Review Count Distribution by Rank Tier\n(Outliers beyond 95th percentile trimmed for visibility)', fontsize=13, fontweight='bold')
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart2_review_by_tier_boxplot.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

# --- Chart 3: Probability of Top-20 by Review Bucket ---
print("  Chart 3: Probability of Top-20 by Review Bucket")
fig, ax = plt.subplots(figsize=(14, 7))
for i, (cat, res) in enumerate(results.items()):
    bp = res['bucket_probs'].reset_index()
    # Only plot buckets with enough data
    bp = bp[bp['count'] >= 3]
    if len(bp) >= 3:
        ax.plot(range(len(bp)), bp['mean'], 'o-', color=CB_PALETTE[i], label=cat, linewidth=1.8, markersize=6)
ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, linewidth=1, label='P=0.5 threshold')
ax.set_xticks(range(8))
ax.set_xticklabels(['0-10', '11-25', '26-50', '51-100', '101-250', '251-500', '501-1000', '1000+'])
ax.set_xlabel('Review Count Bucket')
ax.set_ylabel('Probability of Top-20 Rank')
ax.set_title('Probability of Breaking into Top 20 by Review Count\n(The "Review Moat" Curve)', fontsize=14, fontweight='bold')
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8, title='Category')
ax.set_ylim(0, 1)
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart3_probability_curve.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

# --- Chart 4: The Review Moat — Threshold Summary ---
print("  Chart 4: Review Moat Bars")
thresholds = pd.DataFrame([
    {'category': cat, 'review_moat': max(0, res['review_threshold'] or 0)}
    for cat, res in results.items()
]).sort_values('review_moat')

fig, ax = plt.subplots(figsize=(12, 6))
colors_bar = [CB_PALETTE[list(results.keys()).index(c)] for c in thresholds['category']]
bars = ax.barh(thresholds['category'], thresholds['review_moat'], color=colors_bar, edgecolor='white', linewidth=0.5)
# Add value labels
for bar, val in zip(bars, thresholds['review_moat']):
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2, f'{val:.0f}', va='center', fontweight='bold', fontsize=10)
ax.set_xlabel('Review Count Threshold (P(top-20) = 50%)')
ax.set_title('The "Review Moat": Reviews Needed for 50% Probability of Top-20 Rank\n(Lower = easier for new sellers)', fontsize=13, fontweight='bold')
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart4_review_moat_bars.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

# --- Chart 5: Category Accessibility Index ---
print("  Chart 5: Category Accessibility Index")
fig, ax = plt.subplots(figsize=(12, 6))
colors_acc = [CB_PALETTE[list(results.keys()).index(c)] for c in acc_df['category']]
bars = ax.barh(acc_df['category'], acc_df['accessibility_index'], color=colors_acc, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, acc_df['accessibility_index']):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}', va='center', fontweight='bold', fontsize=10)
ax.set_xlabel('Accessibility Index (0-100, higher = easier to enter)')
ax.set_title('Category Accessibility Index\n(Review barrier 40% · Price dispersion 30% · Brand concentration 30%)', fontsize=13, fontweight='bold')
ax.set_xlim(0, 105)
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart5_accessibility_index.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

# --- Chart 6: Price × Reviews Interaction Heatmap ---
print("  Chart 6: Price × Reviews Interaction")
# Bin price and reviews
df['price_bin'] = pd.qcut(df['price_usd'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
df['review_bin'] = pd.qcut(df['review_count'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
heatmap_data = df.pivot_table(values='in_top20', index='review_bin', columns='price_bin', aggfunc='mean')
fig, ax = plt.subplots(figsize=(10, 7))
sns.heatmap(heatmap_data, annot=True, fmt='.0%', cmap='YlOrRd', ax=ax, vmin=0, vmax=0.5, cbar_kws={'label': 'P(Top 20)'})
ax.set_title('Probability of Top-20 Rank: Price × Reviews Interaction\n(All categories combined)', fontsize=13, fontweight='bold')
ax.set_xlabel('Price Tier')
ax.set_ylabel('Review Count Tier')
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart6_price_review_interaction.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

# --- Chart 7: Rating vs Reviews — Which Matters More? ---
print("  Chart 7: Rating vs Reviews Importance")
importance_data = []
for cat in sorted(df['category'].unique()):
    cat_df = df[df['category'] == cat]
    r_reviews = abs(spearmanr(cat_df['review_count'], cat_df['bsr_rank'])[0])
    r_rating = abs(spearmanr(cat_df['rating'], cat_df['bsr_rank'])[0])
    importance_data.append({'category': cat, 'reviews_rho': r_reviews, 'rating_rho': r_rating, 'difference': r_reviews - r_rating})

imp_df = pd.DataFrame(importance_data).sort_values('difference', ascending=True)
fig, ax = plt.subplots(figsize=(12, 7))
x = np.arange(len(imp_df))
width = 0.35
bars1 = ax.barh(x - width/2, imp_df['reviews_rho'], width, label='Review Count |ρ|', color='#0072B2')
bars2 = ax.barh(x + width/2, imp_df['rating_rho'], width, label='Rating |ρ|', color='#E69F00')
ax.set_yticks(x)
ax.set_yticklabels(imp_df['category'])
ax.set_xlabel("Absolute Spearman's ρ with BSR Rank")
ax.set_title('Which Matters More for Rank: Reviews or Rating?\n(Higher bar = stronger relationship)', fontsize=13, fontweight='bold')
ax.legend()
ax.set_xlim(0, 0.5)
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart7_rating_vs_reviews_importance.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

# --- Chart 8: Review Count Distribution by Category (Violin) ---
print("  Chart 8: Review Distribution Violin Plot")
fig, ax = plt.subplots(figsize=(14, 7))
cat_order = sorted(df['category'].unique())
# Trim to 95th percentile for visibility
p95 = df['review_count'].quantile(0.95)
violin_data = [df[df['category']==c]['review_count'].clip(upper=p95).values for c in cat_order]
parts = ax.violinplot(violin_data, positions=range(len(cat_order)), showmeans=True, showmedians=True)
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(CB_PALETTE[i])
    pc.set_alpha(0.7)
ax.set_xticks(range(len(cat_order)))
ax.set_xticklabels(cat_order, rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Review Count')
ax.set_title(f'Review Count Distribution by Category\n(Trimmed at 95th percentile = {p95:,.0f} reviews)', fontsize=13, fontweight='bold')
plt.tight_layout()
fig.savefig(f"{VIZ_DIR}/{DATE}_chart8_review_distribution_violin.png", bbox_inches='tight', dpi=150)
plt.close()
print("    [OK] Saved")

print("\n[OK] All 8 visualizations saved.")

# ── SURPRISE FINDINGS ──────────────────────────────────
print("\n" + "=" * 70)
print("5. KEY FINDINGS & SURPRISES")
print("=" * 70)

# Finding 1: Categories with lowest review barriers
print("\n[FIND] FINDING 1: Lowest Review Barriers")
low_barrier = cat_summary.sort_values('pct_under_50', ascending=False)
print(low_barrier[['pct_under_50', 'pct_under_100', 'median_reviews']].head(5).to_string())

# Finding 2: Review moat thresholds
print("\n[FIND] FINDING 2: Review Moat Thresholds")
threshold_df = thresholds.set_index('category')
print(threshold_df.to_string())

# Finding 3: Rating vs Reviews
print("\n[FIND] FINDING 3: Where Rating Matters More Than Reviews")
rating_wins = imp_df[imp_df['difference'] < 0]
if len(rating_wins) > 0:
    print(f"Categories where RATING is more predictive than reviews: {rating_wins['category'].tolist()}")
else:
    # Find where the gap is smallest
    closest = imp_df.nsmallest(3, 'difference')
    print(f"Categories where rating almost matters as much: {closest['category'].tolist()}")

# Finding 4: Price×Review interaction
print("\n[FIND] FINDING 4: Price-Review Interaction")
print(heatmap_data.to_string())

# Finding 5: Overall
# How many categories have 30%+ of top 100 with under 50 reviews
low_barrier_cats = cat_summary[cat_summary['pct_under_50'] >= 30]
print(f"\n[FIND] FINDING 5: {len(low_barrier_cats)}/{len(cat_summary)} categories have 30%+ of top-100 products with <50 reviews")
print(low_barrier_cats[['pct_under_50', 'pct_under_100']].to_string())

# Overall stats
print(f"\n[STAT] OVERALL: Across all 10 categories:")
print(f"  % of top-100 with <50 reviews: {cat_summary['pct_under_50'].mean():.1f}%")
print(f"  % of top-100 with <100 reviews: {cat_summary['pct_under_100'].mean():.1f}%")
print(f"  Median review moat threshold: {thresholds['review_moat'].median():.0f}")
print(f"  Easiest category: {acc_df.iloc[0]['category']} (Index={acc_df.iloc[0]['accessibility_index']:.1f})")
print(f"  Hardest category: {acc_df.iloc[-1]['category']} (Index={acc_df.iloc[-1]['accessibility_index']:.1f})")

print("\n[OK] Analysis complete!")
