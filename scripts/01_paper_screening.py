# Cell 1: Load papers
import pandas as pd

papers = pd.read_csv('data/raw/tropism_papers_to_review.csv')
print(f"Total papers to review: {len(papers)}")

# Sort by relevance
papers = papers.sort_values('relevance_score', ascending=False)
papers.head(20)

# Cell 2: Screening criteria
"""
INCLUDE if paper has:
✓ Quantitative tropism/biodistribution data
✓ Multiple tissues compared
✓ Clear methods (dose, route, timepoint)
✓ Mouse, NHP, or human data

EXCLUDE if paper:
✗ Only one tissue
✗ No quantitative data
✗ Review/commentary only
✗ In vitro only
"""

# Cell 3: Mark papers for data extraction
papers['include'] = False  # Start with all False
papers['priority'] = 0  # 1=high, 2=medium, 3=low

# Mark high priority papers (you'll do this manually)
high_priority_pmids = [
    '18432245',  # Zincarelli 2008 - THE seminal paper
    '26814963',  # Deverman 2016 - AAV-PHP
    '20179071',  # Asokan 2012 - AAV evolution
    # Add more as you screen
]

papers.loc[papers['pmid'].isin(high_priority_pmids), 'include'] = True
papers.loc[papers['pmid'].isin(high_priority_pmids), 'priority'] = 1

# Cell 4: Save screening results
papers.to_csv('data/processed/papers_screened.csv', index=False)

included = papers[papers['include'] == True]
print(f"\n✓ Papers marked for data extraction: {len(included)}")
print(f"  High priority: {sum(papers['priority'] == 1)}")
print(f"  Medium priority: {sum(papers['priority'] == 2)}")