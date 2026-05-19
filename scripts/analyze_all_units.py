"""
Analyze all units in your extracted data
Run this AFTER extraction is complete
"""
import pandas as pd
import numpy as np

def analyze_all_units(input_file='data/metadata/tropism_extraction_template_enhanced.xlsx'):
    """
    Show all units used and their value ranges
    """
    
    print("="*70)
    print("UNIT ANALYSIS - COMPLETE DATASET")
    print("="*70)
    
    # Load data
    df = pd.read_excel(input_file, sheet_name='Data')
    print(f"\nTotal data points: {len(df)}")
    
    # Remove empty rows
    df = df[df['raw_value'].notna()]
    print(f"Data points with values: {len(df)}")
    
    # Group by measurement method and units
    print("\n" + "="*70)
    print("UNITS BY MEASUREMENT METHOD")
    print("="*70)
    
    for method in df['measurement_method'].unique():
        if pd.isna(method):
            continue
            
        method_data = df[df['measurement_method'] == method]
        
        print(f"\n{method}:")
        print(f"  Total data points: {len(method_data)}")
        
        # Show units used
        units_summary = method_data.groupby('units').agg({
            'raw_value': ['count', 'min', 'max']
        })
        
        for units in method_data['units'].unique():
            if pd.isna(units):
                continue
                
            unit_data = method_data[method_data['units'] == units]
            
            # Convert to numeric
            numeric_values = pd.to_numeric(unit_data['raw_value'], errors='coerce').dropna()
            
            if len(numeric_values) > 0:
                print(f"\n  Units: {units}")
                print(f"    Count: {len(numeric_values)}")
                print(f"    Range: {numeric_values.min():.2e} to {numeric_values.max():.2e}")
                print(f"    Mean: {numeric_values.mean():.2e}")
                print(f"    Median: {numeric_values.median():.2e}")
                
                # Suggest normalization range
                if len(numeric_values) > 5:
                    log_values = np.log10(numeric_values[numeric_values > 0])
                    if len(log_values) > 0:
                        log_min = np.floor(log_values.min())
                        log_max = np.ceil(log_values.max())
                        print(f"    Suggested log range: {int(log_min)} to {int(log_max)}")
    
    # Summary table
    print("\n" + "="*70)
    print("SUMMARY: ALL UNIQUE UNITS")
    print("="*70)
    
    all_units = df['units'].value_counts()
    print("\nUnit frequency:")
    for units, count in all_units.items():
        print(f"  {units}: {count} data points")
    
    # Save to file
    output_file = 'data/metadata/units_analysis.txt'
    with open(output_file, 'w') as f:
        f.write("UNIT ANALYSIS\n")
        f.write("="*70 + "\n\n")
        for units, count in all_units.items():
            f.write(f"{units}: {count}\n")
    
    print(f"\n✓ Saved analysis to: {output_file}")

if __name__ == "__main__":
    analyze_all_units()