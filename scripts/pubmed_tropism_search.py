"""
Comprehensive PubMed search for AAV tropism studies
"""
from Bio import Entrez
import pandas as pd
import time
import json
from datetime import datetime

Entrez.email = "your.personal@email.com"

def search_pubmed_tropism():
    """Search for AAV tropism papers"""
    
    # Comprehensive search queries
    queries = [
        '("AAV" OR "adeno-associated virus") AND ("tropism" OR "biodistribution")',
        '("AAV" OR "adeno-associated virus") AND ("tissue distribution" OR "transduction")',
        '("AAV serotype") AND ("expression" OR "targeting")',
        '("AAV1" OR "AAV2" OR "AAV3" OR "AAV4" OR "AAV5" OR "AAV6" OR "AAV7" OR "AAV8" OR "AAV9") AND ("tissue" OR "organ")',
        '("AAV-PHP" OR "AAV9" OR "AAVrh10") AND ("brain" OR "CNS" OR "liver" OR "muscle")',
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
                maxdate="2024"
            )
            record = Entrez.read(handle)
            handle.close()
            
            pmids = record["IdList"]
            all_pmids.update(pmids)
            print(f"  Found {len(pmids)} articles")
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    print(f"\n✓ Total unique articles: {len(all_pmids)}")
    return list(all_pmids)

def fetch_article_details(pmids, batch_size=50):
    """Fetch detailed information for articles"""
    
    articles = []
    
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        print(f"Fetching batch {i//batch_size + 1}/{len(pmids)//batch_size + 1}...")
        
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
                    
                    # Extract info
                    article_dict = {
                        'pmid': str(record['MedlineCitation']['PMID']),
                        'title': article.get('ArticleTitle', ''),
                        'journal': article['Journal']['Title'],
                        'year': article['Journal']['JournalIssue']['PubDate'].get('Year', ''),
                        'abstract': '',
                        'authors': []
                    }
                    
                    # Abstract
                    if 'Abstract' in article:
                        abstract_texts = article['Abstract'].get('AbstractText', [])
                        if abstract_texts:
                            article_dict['abstract'] = ' '.join([str(text) for text in abstract_texts])
                    
                    # Authors (first 3)
                    if 'AuthorList' in article:
                        for author in article['AuthorList'][:3]:
                            if 'LastName' in author:
                                article_dict['authors'].append(author['LastName'])
                    
                    articles.append(article_dict)
                    
                except Exception as e:
                    print(f"  Error parsing article: {e}")
                    continue
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error fetching batch: {e}")
            continue
    
    return articles

def screen_articles(articles):
    """Screen articles for relevance"""
    
    # Keywords indicating tropism/biodistribution studies
    relevant_keywords = [
        'tropism', 'biodistribution', 'tissue distribution',
        'transduction', 'expression', 'targeting',
        'liver', 'brain', 'muscle', 'heart', 'lung', 'kidney',
        'CNS', 'peripheral', 'systemic', 'local'
    ]
    
    screened = []
    
    for article in articles:
        text = (article['title'] + ' ' + article['abstract']).lower()
        
        # Check for relevant keywords
        relevance_score = sum(1 for kw in relevant_keywords if kw in text)
        
        # Must have at least 2 relevant keywords
        if relevance_score >= 2:
            article['relevance_score'] = relevance_score
            screened.append(article)
    
    return screened

def main():
    """Main pipeline"""
    
    print("="*70)
    print("AAV Tropism Meta-Analysis: Literature Search")
    print("="*70)
    
    # Search PubMed
    pmids = search_pubmed_tropism()
    
    # Fetch details
    print("\nFetching article details...")
    articles = fetch_article_details(pmids)
    
    # Screen for relevance
    print("\nScreening articles for relevance...")
    screened = screen_articles(articles)
    
    # Save results
    output_file = f"data/raw/tropism_papers_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(screened, f, indent=2)
    
    # Create CSV for manual review
    df = pd.DataFrame(screened)
    df = df.sort_values('relevance_score', ascending=False)
    df.to_csv('data/raw/tropism_papers_to_review.csv', index=False)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total articles found: {len(articles)}")
    print(f"Relevant articles: {len(screened)}")
    print(f"Saved to: {output_file}")
    print(f"\nTop journals:")
    
    journal_counts = df['journal'].value_counts().head(10)
    for journal, count in journal_counts.items():
        print(f"  {journal}: {count}")
    
    print(f"\nYear distribution:")
    year_counts = df['year'].value_counts().sort_index(ascending=False).head(10)
    for year, count in year_counts.items():
        print(f"  {year}: {count}")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("1. Review: data/raw/tropism_papers_to_review.csv")
    print("2. Download PDFs for top 100 papers")
    print("3. Extract tropism data manually")
    print("="*70)

if __name__ == "__main__":
    main()