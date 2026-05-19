"""
AAV Tropism Meta-Analysis: Comprehensive PubMed Literature Search
Optimized for finding high-quality tropism and biodistribution studies
"""
from Bio import Entrez
import pandas as pd
import time
import json
from datetime import datetime

# Configure Entrez
Entrez.email = "your.personal@email.com"

def search_pubmed_tropism():
    """
    Execute comprehensive PubMed search for AAV tropism studies
    
    Returns:
        list: Unique PMIDs from all search queries
    """
    
    queries = [
        # Core tropism and biodistribution
        '("AAV" OR "adeno-associated virus" OR "adeno associated virus") AND ("tropism" OR "biodistribution")',
        
        # Tissue and organ distribution
        '("AAV" OR "adeno-associated virus") AND ("tissue distribution" OR "organ distribution")',
        '("AAV" OR "adeno-associated virus") AND ("transduction" OR "gene transfer" OR "gene delivery")',
        
        # Serotype comparison studies (critical for meta-analysis)
        '("AAV serotype" OR "AAV serotypes") AND ("comparison" OR "comparative" OR "analysis")',
        '("AAV1" OR "AAV2" OR "AAV3" OR "AAV4" OR "AAV5" OR "AAV6" OR "AAV7" OR "AAV8" OR "AAV9") AND ("serotype" OR "serotypes") AND ("tissue" OR "organ" OR "expression")',
        
        # Tissue-specific targeting
        '("AAV" OR "adeno-associated virus") AND ("liver" OR "hepatic") AND ("transduction" OR "expression")',
        '("AAV" OR "adeno-associated virus") AND ("brain" OR "CNS" OR "neural" OR "neuronal") AND ("transduction" OR "expression")',
        '("AAV" OR "adeno-associated virus") AND ("muscle" OR "cardiac" OR "heart") AND ("transduction" OR "expression")',
        '("AAV" OR "adeno-associated virus") AND ("kidney" OR "renal" OR "lung" OR "pulmonary")',
        
        # Systemic administration studies
        '("AAV" OR "adeno-associated virus") AND ("systemic" OR "intravenous" OR "IV injection")',
        
        # Gene expression patterns
        '("AAV" OR "adeno-associated virus") AND ("gene expression" OR "transgene expression") AND ("tissue" OR "organ")',
        
        # Engineered variants
        '("AAV-PHP" OR "AAVrh10" OR "AAV2/8" OR "AAV2/9" OR "MyoAAV1A" OR "MyoAAV2A" OR "MyoAAV3A" OR "MyoAAV4A" OR "AAVMYO") AND ("brain" OR "CNS" OR "liver" OR "muscle")',
        
        # Vector comparison studies
        '("AAV vector" OR "AAV vectors") AND ("comparison" OR "comparative") AND ("efficiency" OR "transduction")',
    ]
    
    all_pmids = set()
    
    for query in queries:
        print(f"\nSearching: {query[:80]}...")
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=500,
                mindate="2000",
                maxdate="2025"
            )
            record = Entrez.read(handle)
            handle.close()
            
            pmids = record["IdList"]
            all_pmids.update(pmids)
            print(f"  Found {len(pmids)} articles (total unique: {len(all_pmids)})")
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    print(f"\n✓ Total unique articles: {len(all_pmids)}")
    return list(all_pmids)

def fetch_article_details(pmids, batch_size=50):
    """
    Fetch detailed metadata for PubMed articles
    
    Args:
        pmids (list): List of PubMed IDs
        batch_size (int): Number of articles to fetch per request
        
    Returns:
        list: Article metadata dictionaries
    """
    
    articles = []
    total_batches = (len(pmids) - 1) // batch_size + 1
    
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"Fetching batch {batch_num}/{total_batches}...")
        
        try:
            handle = Entrez.efetch(
                db="pubmed",
                id=batch,
                rettype="xml"
            )
            records = Entrez.read(handle)
            handle.close()
            
            for record in records['PubmedArticle']:
                try:
                    article = record['MedlineCitation']['Article']
                    
                    # Extract basic metadata
                    article_dict = {
                        'pmid': str(record['MedlineCitation']['PMID']),
                        'title': article.get('ArticleTitle', ''),
                        'journal': article['Journal']['Title'],
                        'year': article['Journal']['JournalIssue']['PubDate'].get('Year', ''),
                        'abstract': '',
                        'authors': []
                    }
                    
                    # Extract abstract
                    if 'Abstract' in article:
                        abstract_texts = article['Abstract'].get('AbstractText', [])
                        if abstract_texts:
                            article_dict['abstract'] = ' '.join([str(text) for text in abstract_texts])
                    
                    # Extract first 3 authors
                    if 'AuthorList' in article:
                        for author in article['AuthorList'][:3]:
                            if 'LastName' in author:
                                article_dict['authors'].append(author['LastName'])
                    
                    articles.append(article_dict)
                    
                except Exception as e:
                    print(f"  Error parsing article: {e}")
                    continue
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  Error fetching batch: {e}")
            continue
    
    return articles

def screen_articles_two_tier(articles):
    """
    Two-tier screening system for article relevance
    
    Tier 1: High-confidence tropism studies (ready for data extraction)
    Tier 2: Potentially relevant (requires manual review)
    
    Args:
        articles (list): List of article dictionaries
        
    Returns:
        tuple: (tier1_papers, tier2_papers, excluded_papers)
    """
    
    # Tier 1 indicators: High-confidence tropism studies
    tier1_indicators = [
        'tropism',
        'biodistribution',
        'tissue distribution',
        'serotype comparison',
        'serotypes 1-9',
        'serotypes 1 through 9',
        'comparative analysis of aav',
        'gene delivery of adeno-associated virus serotypes',
        'transduction efficiency',
        'vector comparison'
    ]
    
    # Tier 2 indicators: Potentially relevant studies
    tier2_indicators = [
        'transduction',
        'gene expression',
        'transgene expression',
        'tissue-specific',
        'organ-specific',
        'systemic injection',
        'intravenous administration',
        'iv injection',
        'systemic delivery'
    ]
    
    # Tissue keywords
    tissue_keywords = [
        'liver', 'brain', 'muscle', 'heart', 'lung', 'kidney',
        'CNS', 'hepatic', 'cardiac', 'neural', 'skeletal muscle',
        'myocardium', 'cerebral', 'cortex', 'striatum', 'spinal cord'
    ]
    
    # AAV-specific keywords (required)
    serotype_keywords = [
        'aav1', 'aav2', 'aav3', 'aav4', 'aav5', 'aav6', 'aav7', 'aav8', 'aav9',
        'serotype', 'serotypes', 'aav-php', 'aavrh10', 'aav2/8', 'aav2/9',
        'myoaav1a', 'myoaav2a', 'myoaav3a', 'myoaav4a', 'aavmyo',
        'adeno-associated virus'
    ]
    
    # Hard exclusion keywords (irrelevant topics)
    hard_exclusion_keywords = [
        'herbal', 'ammonia', 'phenol', 'papaya', 'schizophrenia',
        'glucocorticoid', 'chromosome segregation', 'menopausal',
        'collateral artery', 'baculovirus', 'lentivirus', 'retrovirus',
        'adenovirus', 'perfusion', 'cavitation', 'furin', 'insulin'
    ]
    
    # Title exclusion keywords (non-research articles)
    title_exclusion_keywords = [
        'overview', 'perspective', 'commentary', 'editorial',
        'letter to', 'reply to', 'correction', 'erratum',
        'retraction', 'book review', 'meeting report'
    ]
    
    # Review indicators
    review_indicators = [
        'review', 'mini-review', 'minireview', 'state of the art',
        'recent advances', 'current status', 'progress in', 'update on'
    ]
    
    tier1_papers = []
    tier2_papers = []
    excluded_papers = []
    
    for article in articles:
        title = article['title'].lower()
        abstract = article['abstract'].lower()
        text = title + ' ' + abstract
        
        # Step 1: Hard exclusions (completely irrelevant)
        if any(kw in text for kw in hard_exclusion_keywords):
            article['exclusion_reason'] = 'Irrelevant topic'
            excluded_papers.append(article)
            continue
        
        # Step 2: Title exclusions (non-research)
        if any(kw in title for kw in title_exclusion_keywords):
            article['exclusion_reason'] = 'Non-research article'
            excluded_papers.append(article)
            continue
        
        # Step 3: Must contain AAV-related terms
        has_aav = any(kw in text for kw in serotype_keywords)
        if not has_aav:
            article['exclusion_reason'] = 'No AAV terms'
            excluded_papers.append(article)
            continue
        
        # Step 4: Review detection
        is_review = False
        review_confidence = 0
        
        for indicator in review_indicators:
            if indicator in title:
                review_confidence += 3
            elif indicator in abstract[:200]:
                review_confidence += 1
        
        if 'we review' in abstract or 'this review' in abstract:
            review_confidence += 2
        
        # Check for methods/data (indicates original research)
        has_methods = any(kw in abstract for kw in [
            'methods', 'materials and methods', 'experimental',
            'we measured', 'we analyzed', 'we performed',
            'we injected', 'we administered', 'mice were',
            'animals were'
        ])
        
        has_data = any(kw in abstract for kw in [
            'data', 'results showed', 'we found', 'we observed',
            'demonstrated', 'figure', 'table', 'n =', 'p <'
        ])
        
        # Exclude reviews without data
        if review_confidence >= 3:
            if not (has_methods and has_data):
                if 'systematic review' not in text and 'meta-analysis' not in text:
                    article['exclusion_reason'] = f'Review paper (confidence: {review_confidence})'
                    excluded_papers.append(article)
                    continue
        
        # Step 5: Match tier indicators
        tier1_matches = [kw for kw in tier1_indicators if kw in text]
        tier2_matches = [kw for kw in tier2_indicators if kw in text]
        tissue_matches = [kw for kw in tissue_keywords if kw in text]
        
        # Calculate relevance scores
        tier1_score = len(tier1_matches) * 5
        tier2_score = len(tier2_matches) * 2
        tissue_score = min(len(tissue_matches), 3)
        total_score = tier1_score + tier2_score + tissue_score
        
        # Classify into tiers
        if tier1_matches:
            # Tier 1: High confidence
            article['tier'] = 1
            article['relevance_score'] = total_score
            article['matched_keywords'] = ', '.join(tier1_matches + tier2_matches[:3])
            article['tissues_mentioned'] = ', '.join(tissue_matches[:5])
            tier1_papers.append(article)
            
        elif len(tier2_matches) >= 2 and len(tissue_matches) >= 2:
            # Tier 2: Potentially relevant
            article['tier'] = 2
            article['relevance_score'] = total_score
            article['matched_keywords'] = ', '.join(tier2_matches)
            article['tissues_mentioned'] = ', '.join(tissue_matches[:5])
            tier2_papers.append(article)
            
        else:
            article['exclusion_reason'] = 'Insufficient relevance'
            excluded_papers.append(article)
    
    return tier1_papers, tier2_papers, excluded_papers

def prioritize_papers(tier1_papers, tier2_papers):
    """
    Calculate priority scores for papers within each tier
    
    Args:
        tier1_papers (list): Tier 1 papers
        tier2_papers (list): Tier 2 papers
        
    Returns:
        tuple: (prioritized_tier1, prioritized_tier2)
    """
    
    high_impact_journals = [
        'molecular therapy', 'gene therapy', 'human gene therapy',
        'nature', 'science', 'cell', 'pnas', 'journal of virology',
        'human molecular genetics'
    ]
    
    for paper in tier1_papers + tier2_papers:
        priority_score = paper['relevance_score']
        text = paper['title'].lower() + paper['abstract'].lower()
        
        # Journal impact boost
        if any(journal in paper['journal'].lower() for journal in high_impact_journals):
            priority_score += 10
        
        # Recency boost
        try:
            year = int(paper['year'])
            if year >= 2020:
                priority_score += 5
            elif year >= 2015:
                priority_score += 3
        except:
            pass
        
        # Multiple serotypes boost
        serotype_count = sum(1 for i in range(1, 10) if f'aav{i}' in text)
        if serotype_count >= 3:
            priority_score += 8
        
        # Comparison study boost
        if 'comparison' in paper['title'].lower() or 'comparative' in paper['title'].lower():
            priority_score += 10
        
        # Comprehensive serotype study boost
        if any(phrase in text for phrase in [
            'serotypes 1-9', 'serotypes 1 through 9', 'aav1-9', 
            'aav 1-9', 'myoaav', 'aavmyo'
        ]):
            priority_score += 15
        
        paper['priority_score'] = priority_score
    
    # Sort by priority
    tier1_papers.sort(key=lambda x: x['priority_score'], reverse=True)
    tier2_papers.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return tier1_papers, tier2_papers

def generate_summary_report(df_tier1, df_tier2, df_excluded):
    """
    Generate and print summary statistics
    
    Args:
        df_tier1 (DataFrame): Tier 1 papers
        df_tier2 (DataFrame): Tier 2 papers
        df_excluded (DataFrame): Excluded papers
    """
    
    print("\n" + "="*70)
    print("TIER 1 - TOP 20 PAPERS")
    print("="*70)
    
    for idx, row in df_tier1.head(20).iterrows():
        authors = ', '.join(row['authors']) if row['authors'] else 'Unknown'
        print(f"{row['priority_score']:3.0f} | {row['year']} | {authors:20s} | {row['title'][:60]}...")
    
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(f"Tier 1 (High confidence): {len(df_tier1)} papers")
    print(f"Tier 2 (Manual review): {len(df_tier2)} papers")
    print(f"Excluded: {len(df_excluded)} papers")
    
    if len(df_excluded) > 0 and 'exclusion_reason' in df_excluded.columns:
        print("\nExclusion breakdown:")
        exclusion_counts = df_excluded['exclusion_reason'].value_counts()
        for reason, count in exclusion_counts.items():
            print(f"  {reason}: {count}")
    
    print(f"\nTop Tier 1 journals:")
    journal_counts = df_tier1['journal'].value_counts().head(10)
    for journal, count in journal_counts.items():
        print(f"  {journal}: {count}")
    
    print(f"\nTier 1 year distribution:")
    year_counts = df_tier1['year'].value_counts().sort_index(ascending=False).head(10)
    for year, count in year_counts.items():
        print(f"  {year}: {count}")
    
    # Check for key papers
    print("\n" + "="*70)
    print("KEY PAPER VERIFICATION")
    print("="*70)
    
    cardiac = df_tier1[df_tier1['title'].str.contains('Comparative cardiac', case=False, na=False)]
    if len(cardiac) > 0:
        print("✓ Found cardiac comparison paper:")
        for idx, row in cardiac.iterrows():
            print(f"  {row['priority_score']:3.0f} | {row['year']} | {row['title']}")
    else:
        print("⚠ Cardiac comparison paper not found in Tier 1")
    
    serotype_comp = df_tier1[df_tier1['title'].str.contains(
        'serotypes.*1.*9|serotype.*comparison', case=False, na=False
    )]
    if len(serotype_comp) > 0:
        print("\n✓ Found serotype comparison papers:")
        for idx, row in serotype_comp.head(5).iterrows():
            print(f"  {row['priority_score']:3.0f} | {row['year']} | {row['title'][:70]}...")

def main():
    """
    Main execution pipeline
    """
    
    print("="*70)
    print("AAV Tropism Meta-Analysis: Literature Search")
    print("="*70)
    
    # Step 1: Search PubMed
    pmids = search_pubmed_tropism()
    
    # Step 2: Fetch article details
    print("\nFetching article details...")
    articles = fetch_article_details(pmids)
    print(f"Total articles fetched: {len(articles)}")
    
    # Step 3: Two-tier screening
    print("\nApplying two-tier screening...")
    tier1_papers, tier2_papers, excluded_papers = screen_articles_two_tier(articles)
    
    print(f"\nScreening results:")
    print(f"  Tier 1 (High confidence): {len(tier1_papers)}")
    print(f"  Tier 2 (Manual review): {len(tier2_papers)}")
    print(f"  Excluded: {len(excluded_papers)}")
    
    # Step 4: Prioritize papers
    print("\nPrioritizing papers...")
    tier1_papers, tier2_papers = prioritize_papers(tier1_papers, tier2_papers)
    
    # Step 5: Save results
    print("\nSaving results...")
    screened = tier1_papers + tier2_papers + excluded_papers
    # Save results
    output_file = f"data/raw/tropism_papers_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(screened, f, indent=2)
    
    df_tier1 = pd.DataFrame(tier1_papers).sort_values('priority_score', ascending=False)
    df_tier2 = pd.DataFrame(tier2_papers).sort_values('priority_score', ascending=False)
    df_excluded = pd.DataFrame(excluded_papers)
    
    df_tier1.to_csv('data/raw/tropism_papers_TIER1_high_confidence.csv', index=False)
    df_tier2.to_csv('data/raw/tropism_papers_TIER2_manual_review.csv', index=False)
    df_excluded.to_csv('data/raw/tropism_papers_EXCLUDED.csv', index=False)
    
    # Step 6: Generate summary report
    generate_summary_report(df_tier1, df_tier2, df_excluded)
    
    print("\n" + "="*70)
    print("FILES CREATED")
    print("="*70)
    print(f"✓ data/raw/tropism_papers_TIER1_high_confidence.csv ({len(tier1_papers)} papers)")
    print(f"✓ data/raw/tropism_papers_TIER2_manual_review.csv ({len(tier2_papers)} papers)")
    print(f"✓ data/raw/tropism_papers_EXCLUDED.csv ({len(excluded_papers)} papers)")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Review top 50 Tier 1 papers")
    print("2. Start extracting tropism data from high-priority papers")
    print("3. Target: 200-300 data points from Tier 1")
    print("="*70)

if __name__ == "__main__":
    main()