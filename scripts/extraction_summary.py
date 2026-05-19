
"""
Quick summary of extracted data
"""
import pandas as pd

def extraction_summary():
    """Show extraction progress"""
    
    df = pd.read_excel('data/metadata/tropism_extraction_template_enhanced.xlsx', 
                       sheet_name='Data')
    
    print("="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)
    
    print(f"\nTotal rows: {len(df)}")
    print(f"Rows with data: {df['raw_value'].notna().sum()}")
    print(f"Unique papers: {df['pmid'].nunique()}")
    print(f"Unique serotypes: {df['serotype'].nunique()}")
    print(f"Unique tissues: {df['tissue'].nunique()}")
    
    print("\nTop 10 serotypes:")
    print(df['serotype'].value_counts().head(10))
    
    print("\nTop 10 tissues:")
    print(df['tissue'].value_counts().head(10))
    
    print("\nMeasurement methods:")
    print(df['measurement_method'].value_counts())
    
    print("\nSpecies:")
    print(df['species'].value_counts())

if __name__ == "__main__":
    extraction_summary()