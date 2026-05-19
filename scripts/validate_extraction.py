"""
Validate extracted tropism data for quality and consistency
Plots the summary of all extracted data points...in figures folder
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_extraction_data(filepath='data/metadata/tropism_extraction_template_enhanced_working.xlsx'):
    """Load data from extraction template"""
    try:
        df = pd.read_excel(filepath, sheet_name='Data')
        print(f"✓ Loaded {len(df)} data points from {filepath}")
        return df
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return None

def validate_required_fields(df):
    """Check that all required fields are present"""
    
    required_fields = [
        'pmid', 'first_author', 'year', 'serotype', 'tissue',
        'species', 'raw_value', 'units'
    ]
    
    print("\n" + "="*70)
    print("REQUIRED FIELDS CHECK")
    print("="*70)
    
    missing_data = {}
    for field in required_fields:
        missing = df[field].isna().sum()
        if missing > 0:
            missing_data[field] = missing
            print(f"⚠ {field}: {missing} missing values ({missing/len(df)*100:.1f}%)")
        else:
            print(f"✓ {field}: Complete")
    
    return len(missing_data) == 0

def validate_value_ranges(df):
    """Check that values are in expected ranges"""
    
    print("\n" + "="*70)
    print("VALUE RANGE CHECK")
    print("="*70)
    
    issues = []
    
    # Check normalized scores (should be 0-5)
    if 'normalized_score' in df.columns:
        out_of_range = df[(df['normalized_score'] < 0) | (df['normalized_score'] > 5)]
        if len(out_of_range) > 0:
            print(f"⚠ {len(out_of_range)} normalized scores out of range (0-5)")
            issues.append('normalized_score_range')
        else:
            print(f"✓ All normalized scores in valid range")
    
    # Check years (should be 2000-2025)
    if 'year' in df.columns:
        invalid_years = df[(df['year'] < 2000) | (df['year'] > 2025)]
        if len(invalid_years) > 0:
            print(f"⚠ {len(invalid_years)} invalid years")
            issues.append('invalid_years')
        else:
            print(f"✓ All years valid (2000-2025)")
    
    # Check raw values (should be positive)
    if 'raw_value' in df.columns:
        try:
            df['raw_value_numeric'] = pd.to_numeric(df['raw_value'], errors='coerce')
            negative = df[df['raw_value_numeric'] <= 0]
            if len(negative) > 0:
                print(f"⚠ {len(negative)} negative or zero raw values")
                issues.append('negative_values')
            else:
                print(f"✓ All raw values positive")
        except:
            print(f"⚠ Could not validate raw values (check format)")
    
    return len(issues) == 0

def check_consistency(df):
    """Check for internal consistency"""
    
    print("\n" + "="*70)
    print("CONSISTENCY CHECK")
    print("="*70)
    
    # Check if same paper has consistent metadata
    paper_groups = df.groupby('pmid')
    
    inconsistent_papers = []
    for pmid, group in paper_groups:
        # Check if first_author is consistent
        if group['first_author'].nunique() > 1:
            print(f"⚠ PMID {pmid}: Inconsistent first_author")
            inconsistent_papers.append(pmid)
        
        # Check if year is consistent
        if group['year'].nunique() > 1:
            print(f"⚠ PMID {pmid}: Inconsistent year")
            inconsistent_papers.append(pmid)
    
    if len(inconsistent_papers) == 0:
        print("✓ All papers have consistent metadata")
    
    # Check for duplicate entries
    duplicates = df.duplicated(subset=['pmid', 'serotype', 'tissue', 'species'], keep=False)
    if duplicates.sum() > 0:
        print(f"\n⚠ Found {duplicates.sum()} potential duplicate entries")
        print("Review these:")
        print(df[duplicates][['pmid', 'first_author', 'serotype', 'tissue']].head())
    else:
        print("\n✓ No duplicate entries found")
    
    return len(inconsistent_papers) == 0

def generate_summary_stats(df):
    """Generate summary statistics"""
    
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    print(f"\nTotal data points: {len(df)}")
    print(f"Unique papers: {df['pmid'].nunique()}")
    print(f"Unique serotypes: {df['serotype'].nunique()}")
    print(f"Unique tissues: {df['tissue'].nunique()}")
    print(f"Species distribution:")
    for species, count in df['species'].value_counts().items():
        print(f"  {species}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\nQuality distribution:")
    if 'quality_score' in df.columns:
        for quality, count in df['quality_score'].value_counts().items():
            print(f"  {quality}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\nTop 10 serotypes:")
    for serotype, count in df['serotype'].value_counts().head(10).items():
        print(f"  {serotype}: {count}")
    
    print(f"\nTop 10 tissues:")
    for tissue, count in df['tissue'].value_counts().head(10).items():
        print(f"  {tissue}: {count}")

# ============================================================================
# THIS IS THE FUNCTION THAT CREATES THE PLOT
# ============================================================================

def plot_data_overview(df):
    """
    Create overview visualizations
    
    This function generates a 2x2 grid of plots:
    1. Top 10 papers by data points (horizontal bar chart)
    2. Top 15 serotypes (bar chart)
    3. Top 15 tissues (horizontal bar chart)
    4. Distribution of normalized scores (histogram)
    """
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 10
    
    # Create figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # ========================================================================
    # PLOT 1: Data points per paper (top left)
    # ========================================================================
    paper_counts = df['pmid'].value_counts().head(10)
    
    # Create labels with author and year
    labels = []
    for pmid in paper_counts.index:
        author = df[df['pmid'] == pmid]['first_author'].iloc[0]
        year = df[df['pmid'] == pmid]['year'].iloc[0]
        labels.append(f"{author} {year}")
    
    axes[0, 0].barh(range(len(paper_counts)), paper_counts.values, color='steelblue')
    axes[0, 0].set_yticks(range(len(paper_counts)))
    axes[0, 0].set_yticklabels(labels)
    axes[0, 0].set_xlabel('Number of Data Points')
    axes[0, 0].set_title('Top 10 Papers by Data Points', fontweight='bold')
    axes[0, 0].invert_yaxis()  # Highest at top
    
    # ========================================================================
    # PLOT 2: Serotype distribution (top right)
    # ========================================================================
    serotype_counts = df['serotype'].value_counts().head(15)
    
    axes[0, 1].bar(range(len(serotype_counts)), serotype_counts.values, color='coral')
    axes[0, 1].set_xticks(range(len(serotype_counts)))
    axes[0, 1].set_xticklabels(serotype_counts.index, rotation=45, ha='right')
    axes[0, 1].set_ylabel('Number of Data Points')
    axes[0, 1].set_title('Top 15 Serotypes', fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # ========================================================================
    # PLOT 3: Tissue distribution (bottom left)
    # ========================================================================
    tissue_counts = df['tissue'].value_counts().head(15)
    
    axes[1, 0].barh(range(len(tissue_counts)), tissue_counts.values, color='mediumseagreen')
    axes[1, 0].set_yticks(range(len(tissue_counts)))
    axes[1, 0].set_yticklabels(tissue_counts.index)
    axes[1, 0].set_xlabel('Number of Data Points')
    axes[1, 0].set_title('Top 15 Tissues', fontweight='bold')
    axes[1, 0].invert_yaxis()  # Highest at top
    
    # ========================================================================
    # PLOT 4: Normalized score distribution (bottom right)
    # ========================================================================
    if 'normalized_score' in df.columns and df['normalized_score'].notna().sum() > 0:
        scores = df['normalized_score'].dropna()
        
        axes[1, 1].hist(scores, bins=20, edgecolor='black', color='mediumpurple', alpha=0.7)
        axes[1, 1].set_xlabel('Normalized Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Distribution of Normalized Scores', fontweight='bold')
        
        # Add mean line
        mean_score = scores.mean()
        axes[1, 1].axvline(mean_score, color='red', linestyle='--', linewidth=2,
                          label=f'Mean: {mean_score:.2f}')
        
        # Add median line
        median_score = scores.median()
        axes[1, 1].axvline(median_score, color='orange', linestyle='--', linewidth=2,
                          label=f'Median: {median_score:.2f}')
        
        axes[1, 1].legend()
        axes[1, 1].grid(axis='y', alpha=0.3)
    else:
        axes[1, 1].text(0.5, 0.5, 'No normalized scores available',
                       ha='center', va='center', fontsize=12)
        axes[1, 1].set_title('Distribution of Normalized Scores', fontweight='bold')
    
    # ========================================================================
    # Save figure
    # ========================================================================
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs('results/figures', exist_ok=True)
    
    output_path = 'results/figures/extraction_overview.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    print(f"\n✓ Saved visualization: {output_path}")
    
    # Also save as PDF for publications
    pdf_path = 'results/figures/extraction_overview.pdf'
    plt.savefig(pdf_path, bbox_inches='tight')
    print(f"✓ Saved PDF version: {pdf_path}")
    
    plt.close()

# ============================================================================
# Main function
# ============================================================================

def main():
    """Run complete validation"""
    
    print("="*70)
    print("AAV TROPISM DATA VALIDATION")
    print("="*70)
    
    # Load data
    df = load_extraction_data()
    if df is None:
        return
    
    # Run validation checks
    required_ok = validate_required_fields(df)
    ranges_ok = validate_value_ranges(df)
    consistency_ok = check_consistency(df)
    
    # Generate summary
    generate_summary_stats(df)
    
    # Create visualizations (THIS CREATES THE PLOT!)
    plot_data_overview(df)
    
    # Overall assessment
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    if required_ok and ranges_ok and consistency_ok:
        print("✓ All validation checks passed!")
        print("✓ Data is ready for analysis")
    else:
        print("⚠ Some validation checks failed")
        print("⚠ Review issues above before proceeding")
    
    print("="*70)

if __name__ == "__main__":
    main()