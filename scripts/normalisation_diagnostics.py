import pandas as pd
import numpy as np

# Load your data
df = pd.read_excel('data/metadata/tropism_extraction_template_enhanced_working.xlsx', 
                   sheet_name='Data')

print("="*70)
print("RAW DATA ANALYSIS")
print("="*70)

# Filter to valid data
df_valid = df[df['raw_value'].notna()].copy()

# Convert to numeric
df_valid['raw_value_numeric'] = pd.to_numeric(df_valid['raw_value'], errors='coerce')
df_valid = df_valid[df_valid['raw_value_numeric'].notna()]
df_valid = df_valid[df_valid['raw_value_numeric'] > 0]

print(f"\nTotal valid data points: {len(df_valid)}")

# Group by measurement method
print("\n" + "="*70)
print("BY MEASUREMENT METHOD")
print("="*70)

for method in df_valid['measurement_method'].unique():
    method_data = df_valid[df_valid['measurement_method'] == method]
    
    print(f"\n{method}:")
    print(f"  Count: {len(method_data)}")
    print(f"  Min: {method_data['raw_value_numeric'].min():.2e}")
    print(f"  Max: {method_data['raw_value_numeric'].max():.2e}")
    print(f"  Mean: {method_data['raw_value_numeric'].mean():.2e}")
    print(f"  Median: {method_data['raw_value_numeric'].median():.2e}")
    
    # Log range
    log_values = np.log10(method_data['raw_value_numeric'])
    print(f"  Log10 range: {log_values.min():.2f} to {log_values.max():.2f}")
    
    # Show units
    print(f"  Units used: {method_data['units'].unique()}")

# Group by units
print("\n" + "="*70)
print("BY UNITS")
print("="*70)

for units in df_valid['units'].unique():
    unit_data = df_valid[df_valid['units'] == units]
    
    print(f"\n{units}:")
    print(f"  Count: {len(unit_data)}")
    print(f"  Range: {unit_data['raw_value_numeric'].min():.2e} to {unit_data['raw_value_numeric'].max():.2e}")
    
    if len(unit_data) > 0:
        log_values = np.log10(unit_data['raw_value_numeric'])
        print(f"  Log10 range: {log_values.min():.2f} to {log_values.max():.2f}")

# Check normalized scores
print("\n" + "="*70)
print("NORMALIZED SCORES")
print("="*70)

normalized = df_valid[df_valid['normalized_score'].notna()]
print(f"\nNormalized data points: {len(normalized)}")
print(f"Score range: {normalized['normalized_score'].min():.2f} to {normalized['normalized_score'].max():.2f}")
print(f"Mean score: {normalized['normalized_score'].mean():.2f}")
print(f"Median score: {normalized['normalized_score'].median():.2f}")

# Distribution
print("\nScore distribution:")
print(f"  0.0-1.0: {len(normalized[normalized['normalized_score'] < 1])} ({len(normalized[normalized['normalized_score'] < 1])/len(normalized)*100:.1f}%)")
print(f"  1.0-2.0: {len(normalized[(normalized['normalized_score'] >= 1) & (normalized['normalized_score'] < 2)])} ({len(normalized[(normalized['normalized_score'] >= 1) & (normalized['normalized_score'] < 2)])/len(normalized)*100:.1f}%)")
print(f"  2.0-3.0: {len(normalized[(normalized['normalized_score'] >= 2) & (normalized['normalized_score'] < 3)])} ({len(normalized[(normalized['normalized_score'] >= 2) & (normalized['normalized_score'] < 3)])/len(normalized)*100:.1f}%)")
print(f"  3.0-4.0: {len(normalized[(normalized['normalized_score'] >= 3) & (normalized['normalized_score'] < 4)])} ({len(normalized[(normalized['normalized_score'] >= 3) & (normalized['normalized_score'] < 4)])/len(normalized)*100:.1f}%)")
print(f"  4.0-5.0: {len(normalized[normalized['normalized_score'] >= 4])} ({len(normalized[normalized['normalized_score'] >= 4])/len(normalized)*100:.1f}%)")