"""
Quick analysis of Tier 1 papers to prioritize data extraction
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Tier 1 papers
df = pd.read_csv('data/raw/tropism_papers_TIER1_high_confidence.csv')

print("="*70)
print("TIER 1 ANALYSIS")
print("="*70)

print(f"\nTotal Tier 1 papers: {len(df)}")
print(f"Priority score range: {df['priority_score'].min():.0f} - {df['priority_score'].max():.0f}")

# Top 10 papers
print("\n" + "="*70)
print("TOP 10 PAPERS FOR DATA EXTRACTION")
print("="*70)

for idx, row in df.head(10).iterrows():
    authors = ', '.join(eval(row['authors'])) if isinstance(row['authors'], str) else 'Unknown'
    print(f"\n{idx+1}. {row['title']}")
    print(f"   Authors: {authors}")
    print(f"   Journal: {row['journal']}, {row['year']}")
    print(f"   Priority: {row['priority_score']:.0f}")
    print(f"   Keywords: {row['matched_keywords']}")
    print(f"   PMID: {row['pmid']}")

# Identify high-value papers (comparison studies)
print("\n" + "="*70)
print("HIGH-VALUE COMPARISON STUDIES")
print("="*70)

comparison_papers = df[
    df['title'].str.contains('comparison|comparative|serotypes 1', case=False, na=False)
].sort_values('priority_score', ascending=False)

print(f"\nFound {len(comparison_papers)} comparison studies")
print("\nTop 5 comparison papers:")
for idx, row in comparison_papers.head(5).iterrows():
    print(f"  • {row['year']} | {row['title'][:70]}...")
    print(f"    Priority: {row['priority_score']:.0f} | PMID: {row['pmid']}")

# Year distribution
print("\n" + "="*70)
print("YEAR DISTRIBUTION")
print("="*70)

year_counts = df['year'].value_counts().sort_index(ascending=False)
for year, count in year_counts.head(10).items():
    print(f"  {year}: {count} papers")

# Estimate data points
print("\n" + "="*70)
print("ESTIMATED DATA POINTS")
print("="*70)

# Assumptions:
# - Comparison studies (3+ serotypes): ~30-50 data points each
# - Single serotype studies: ~5-10 data points each
# - Target: Top 50 papers

comparison_count = len(comparison_papers.head(20))
single_count = 30

estimated_points = (comparison_count * 40) + (single_count * 7)
print(f"\nEstimated data points from top 50 papers:")
print(f"  {comparison_count} comparison studies × 40 points = {comparison_count * 40}")
print(f"  {single_count} single studies × 7 points = {single_count * 7}")
print(f"  Total estimated: ~{estimated_points} data points")

print("\n✓ Sufficient for meta-analysis (target: 300-500 points)")