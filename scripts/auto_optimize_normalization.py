"""
ADAPTIVE NORMALIZATION - WITH UNIT CONVERSION AND 'NOT DETECTED' HANDLING
Converts vg/µg DNA to vg/diploid genome for consistent normalization
Treats VCN/dg (vector copy number) as equivalent to vg/dg
"""
import pandas as pd
import numpy as np
import sys
import os
import warnings

class AdaptiveNormalizer:
    """
    Normalizer that learns and applies optimal parameters
    Handles unit conversion (vg/µg DNA → vg/dg)
    Treats VCN/dg as equivalent to vg/dg
    """
    
    # Conversion factors: diploid genomes per µg DNA
    CONVERSION_FACTORS = {
        'Mouse': 166667,
        'Rat': 166667,
        'Human': 151515,
        'NHP': 156250,
        'Cynomolgus': 156250,
        'Rhesus': 156250,
        'Macaque': 156250
    }
    
    def __init__(self, df=None):
        # Initialize with empty params
        self.normalization_params = {}
        
        if df is not None:
            self.learn_parameters(df)
    
    def convert_to_vg_dg(self, raw_value, units, species):
        """
        Convert raw value to vg/diploid genome if needed
        
        Args:
            raw_value: Raw measurement value
            units: Unit string (e.g., 'vg/ug DNA', 'vg/dg', 'VCN/dg', etc.)
            species: Species name
        
        Returns:
            Value in vg/diploid genome
        """
        
        if pd.isna(raw_value) or pd.isna(units):
            return raw_value
        
        # Handle string "not detected" values
        if isinstance(raw_value, str):
            return raw_value  # Will be handled by normalize_value
        
        try:
            value = float(raw_value)
        except:
            return raw_value
        
        units_lower = str(units).lower().replace(' ', '').replace('µ', 'u').replace('μ', 'u')
        
        # Already in vg/dg, VCN/dg, or equivalent units (NO CONVERSION NEEDED)
        if any(x in units_lower for x in [
            'vg/dg', 'vcn/dg',  # Standard units
            'vg/diploid', 'vcn/diploid',
            'vg/diploidgenome', 'vcn/diploidgenome',
            'vg/genomecopy', 'vcn/genomecopy',
            'vectorcopy/dg', 'vectorcopies/dg',
            'vg/cell', 'vcn/cell'
        ]):
            return value
        
        # Convert from vg/µg DNA
        if 'vg/ug' in units_lower and 'dna' in units_lower:
            factor = self.CONVERSION_FACTORS.get(species, 166667)  # Default to mouse
            converted = value / factor
            return converted
        
        # Convert from vg/ng DNA
        if 'vg/ng' in units_lower and 'dna' in units_lower:
            factor = self.CONVERSION_FACTORS.get(species, 166667)
            converted = value / (factor / 1000)  # ng to µg
            return converted
        
        # If unit not recognized, return as-is and warn
        if 'vg' in units_lower or 'vcn' in units_lower:
            warnings.warn(f"Unknown qPCR unit: {units}. Assuming vg/dg.")
        
        return value
    
    def standardize_units(self, units):
        """
        Standardize unit names to 'vg/dg'
        Treats VCN/dg, vector copies/dg, etc. as equivalent
        
        Args:
            units: Original unit string
        
        Returns:
            Standardized unit string
        """
        
        if pd.isna(units):
            return units
        
        units_lower = str(units).lower().replace(' ', '').replace('µ', 'u').replace('μ', 'u')
        
        # Standardize all equivalent units to 'vg/dg'
        equivalent_units = [
            'vcn/dg', 'vcn/diploidgenome', 'vcn/diploid',
            'vg/diploidgenome', 'vg/diploid',
            'vectorcopy/dg', 'vectorcopies/dg',
            'vg/genomecopy', 'vcn/genomecopy',
            'vg/cell', 'vcn/cell'
        ]
        
        for equiv in equivalent_units:
            if equiv in units_lower:
                return 'vg/dg'
        
        # Already vg/dg
        if 'vg/dg' in units_lower:
            return 'vg/dg'
        
        # Return original if not recognized
        return units
    
    def learn_parameters(self, df):
        """Learn optimal normalization parameters from data"""
        
        print("Learning normalization parameters from data...")
        print("="*70)
        
        # Filter valid data
        df_valid = df[df['raw_value'].notna()].copy()
        
        # STEP 1: Standardize units (VCN/dg → vg/dg)
        print("\nStep 1: Standardizing unit names...")
        standardization_count = 0
        
        for idx, row in df_valid.iterrows():
            if pd.notna(row.get('units', '')):
                original_units = row['units']
                standardized_units = self.standardize_units(original_units)
                
                if standardized_units != original_units:
                    if standardization_count < 3:  # Show first 3 examples
                        print(f"  Example: '{original_units}' → '{standardized_units}'")
                    df_valid.at[idx, 'units'] = standardized_units
                    standardization_count += 1
        
        if standardization_count > 0:
            print(f"✓ Standardized {standardization_count} unit names to 'vg/dg'")
        else:
            print("  No unit standardization needed")
        
        # STEP 2: Convert units to vg/dg for qPCR data
        print("\nStep 2: Converting vg/ug DNA to vg/dg...")
        conversion_count = 0
        
        for idx, row in df_valid.iterrows():
            if pd.notna(row['raw_value']) and pd.notna(row.get('units', '')):
                units_lower = str(row['units']).lower()
                
                # Only convert qPCR data with vg/ug or vg/ng units
                if 'qpcr' in str(row['measurement_method']).lower() or 'pcr' in str(row['measurement_method']).lower():
                    if 'vg/ug' in units_lower or 'vg/ng' in units_lower:
                        original = row['raw_value']
                        converted = self.convert_to_vg_dg(
                            row['raw_value'],
                            row['units'],
                            row.get('species', 'Mouse')
                        )
                        df_valid.at[idx, 'raw_value'] = converted
                        df_valid.at[idx, 'units'] = 'vg/dg'
                        conversion_count += 1
                        
                        if conversion_count <= 3:  # Show first 3 examples
                            print(f"  Example: {original:.2e} {row['units']} → {converted:.2e} vg/dg ({row.get('species', 'Mouse')})")
        
        if conversion_count > 0:
            print(f"✓ Converted {conversion_count} qPCR values to vg/dg")
        else:
            print("  No unit conversions needed")
        
        # STEP 3: Convert to numeric, excluding "not detected" entries
        print("\nStep 3: Preparing data for parameter learning...")
        
        def safe_float(val):
            if pd.isna(val):
                return np.nan
            if isinstance(val, str):
                val_lower = val.lower().strip()
                # Exclude these from parameter learning (they'll be 0)
                if val_lower in ['nt', 'not tested', 'not measured',
                                'bdl', 'below detection', 'nd', 'not detected',
                                'below detection limit', 'not detectable']:
                    return np.nan
            try:
                return float(val)
            except:
                return np.nan
        
        df_valid['raw_value_numeric'] = df_valid['raw_value'].apply(safe_float)
        
        # Only learn from positive detections (exclude zeros and NaN)
        df_valid = df_valid[df_valid['raw_value_numeric'] > 0]
        
        print(f"Learning from {len(df_valid)} positive detections")
        print("(Excluding 'Not Detected' entries from parameter learning)")
        
        # STEP 4: Learn parameters for each method
        print("\nStep 4: Learning normalization parameters...")
        
        for method in df_valid['measurement_method'].unique():
            method_data = df_valid[df_valid['measurement_method'] == method]['raw_value_numeric']
            
            if len(method_data) < 5:
                print(f"  ⚠ {method}: Too few data points (n={len(method_data)}), skipping")
                continue
            
            # Calculate log values
            log_values = np.log10(method_data)
            
            # Use 5th and 95th percentiles
            p5 = np.percentile(log_values, 5)
            p95 = np.percentile(log_values, 95)
            
            # Round to integers
            log_min = int(np.floor(p5))
            log_max = int(np.ceil(p95))
            log_range = log_max - log_min
            
            # Ensure minimum range of 3
            if log_range < 3:
                log_max = log_min + 3
                log_range = 3
            
            # Store parameters
            self.normalization_params[method] = {
                'log_min': log_min,
                'log_max': log_max,
                'log_range': log_range,
                'use_log': True
            }
            
            print(f"\n  {method}:")
            print(f"    Data points: {len(method_data)}")
            print(f"    Raw range: {method_data.min():.2e} to {method_data.max():.2e}")
            print(f"    Log10 range: {log_values.min():.2f} to {log_values.max():.2f}")
            print(f"    5th percentile (log10): {p5:.2f}")
            print(f"    95th percentile (log10): {p95:.2f}")
            print(f"    → PARAMETERS: log_min={log_min}, log_max={log_max}, range={log_range}")
        
        print("\n✓ Parameters learned!")
    
    def normalize_value(self, raw_value, units, method):
        """
        Normalize using LEARNED parameters
        Handles "Not Detected" as 0.0
        """
        
        # Handle missing/empty values
        if pd.isna(raw_value) or raw_value == '':
            return np.nan
        
        # Handle string values
        if isinstance(raw_value, str):
            raw_value_lower = raw_value.lower().strip()
            
            # Not tested = NaN (missing data)
            if raw_value_lower in ['nt', 'not tested', 'not measured']:
                return np.nan
            
            # Not detected = 0.0 (true zero, tested but not detected)
            if raw_value_lower in ['bdl', 'below detection', 'nd', 'not detected',
                                   'below detection limit', 'not detectable',
                                   'below limit of detection', 'below lod']:
                return 0.0
        
        # Convert to float
        try:
            value = float(raw_value)
        except:
            return np.nan
        
        # Handle zero or negative values
        if value <= 0:
            return 0.0
        
        # Look up learned parameters for this method
        if method in self.normalization_params:
            params = self.normalization_params[method]
            
            # Use learned parameters
            log_value = np.log10(value)
            log_min = params['log_min']
            log_range = params['log_range']
            
            normalized = (log_value - log_min) / log_range * 5
            normalized = np.clip(normalized, 0, 5)
            
            return round(normalized, 2)
        
        # Fallback for methods without learned parameters
        warnings.warn(f"No learned parameters for method '{method}', using default")
        log_value = np.log10(value)
        normalized = (log_value - 6) / 4 * 5
        return round(np.clip(normalized, 0, 5), 2)
    
    def normalize_dataframe(self, df):
        """Normalize all rows with unit conversion and standardization"""
        
        print("Normalizing data with learned parameters...")
        
        # STEP 1: Standardize units (VCN/dg → vg/dg)
        print("\nStep 1: Standardizing unit names in full dataset...")
        standardization_count = 0
        
        for idx, row in df.iterrows():
            if pd.notna(row.get('units', '')):
                original_units = row['units']
                standardized_units = self.standardize_units(original_units)
                
                if standardized_units != original_units:
                    df.at[idx, 'units'] = standardized_units
                    standardization_count += 1
        
        if standardization_count > 0:
            print(f"✓ Standardized {standardization_count} unit names")
        
        # STEP 2: Convert units for qPCR data
        print("\nStep 2: Converting vg/ug DNA to vg/dg...")
        conversion_count = 0
        
        for idx, row in df.iterrows():
            if pd.notna(row['raw_value']) and pd.notna(row.get('units', '')):
                method_lower = str(row['measurement_method']).lower()
                units_lower = str(row['units']).lower()
                
                # Only convert qPCR data with vg/ug or vg/ng units
                if 'qpcr' in method_lower or 'pcr' in method_lower:
                    if 'vg/ug' in units_lower or 'vg/ng' in units_lower:
                        converted = self.convert_to_vg_dg(
                            row['raw_value'],
                            row['units'],
                            row.get('species', 'Mouse')
                        )
                        df.at[idx, 'raw_value'] = converted
                        df.at[idx, 'units'] = 'vg/dg'
                        conversion_count += 1
        
        if conversion_count > 0:
            print(f"✓ Converted {conversion_count} values to vg/dg")
        else:
            print("  No conversions needed")
        
        # STEP 3: Normalize all values
        print("\nStep 3: Normalizing all values...")
        
        if 'normalized_score' not in df.columns:
            df['normalized_score'] = np.nan
        
        normalized_count = 0
        zero_count = 0
        missing_count = 0
        
        for idx, row in df.iterrows():
            if pd.isna(row['raw_value']):
                missing_count += 1
                continue
            
            normalized = self.normalize_value(
                row['raw_value'],
                row['units'],
                row['measurement_method']
            )
            
            df.at[idx, 'normalized_score'] = normalized
            
            if pd.notna(normalized):
                normalized_count += 1
                if normalized == 0.0:
                    zero_count += 1
            else:
                missing_count += 1
        
        print(f"✓ Normalized {normalized_count} data points")
        print(f"  • Detected: {normalized_count - zero_count}")
        print(f"  • Not Detected (zeros): {zero_count}")
        print(f"  • Not Tested (missing): {missing_count}")
        
        return df

def main():
    print("="*70)
    print("ADAPTIVE NORMALIZATION - WITH UNIT CONVERSION")
    print("Handles VCN/dg, vg/dg, and vg/ug DNA units")
    print("="*70)
    
    # Load data
    input_file = 'data/metadata/tropism_extraction_template_enhanced_working.xlsx'
    
    try:
        df = pd.read_excel(input_file, sheet_name='Data')
        print(f"\n✓ Loaded {len(df)} rows")
    except FileNotFoundError:
        print(f"✗ Error: Could not find {input_file}")
        return
    
    df_with_data = df[df['raw_value'].notna()]
    print(f"✓ Found {len(df_with_data)} rows with raw values")
    
    # Count units
    qpcr_data = df_with_data[
        df_with_data['measurement_method'].str.contains('qPCR|PCR', case=False, na=False)
    ]
    
    print(f"\nqPCR data unit breakdown:")
    for units, count in qpcr_data['units'].value_counts().items():
        print(f"  {units}: {count}")
    
    # Count "Not Detected" entries
    not_detected_count = 0
    for val in df_with_data['raw_value']:
        if isinstance(val, str):
            val_lower = val.lower().strip()
            if val_lower in ['bdl', 'below detection', 'nd', 'not detected',
                           'below detection limit', 'not detectable']:
                not_detected_count += 1
    
    print(f"\n  • 'Not Detected' entries: {not_detected_count} (will be normalized to 0)")
    
    # Learn and normalize
    print("\n" + "="*70)
    print("LEARNING PARAMETERS")
    print("="*70)
    normalizer = AdaptiveNormalizer(df)
    
    print("\n" + "="*70)
    print("NORMALIZING")
    print("="*70)
    df = normalizer.normalize_dataframe(df)
    
    # Save
    output_file = 'data/processed/tropism_data_FINAL_normalized.xlsx'
    os.makedirs('data/processed', exist_ok=True)
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Parameters sheet
        params_list = []
        for method, params in normalizer.normalization_params.items():
            params_list.append({
                'Method': method,
                'log_min': params['log_min'],
                'log_max': params['log_max'],
                'log_range': params['log_range']
            })
        
        if params_list:
            params_df = pd.DataFrame(params_list)
            params_df.to_excel(writer, sheet_name='Parameters', index=False)
        
        # Conversion factors sheet
        conversion_df = pd.DataFrame([
            {'Species': species, 'Diploid_Genomes_per_ug_DNA': factor}
            for species, factor in normalizer.CONVERSION_FACTORS.items()
        ])
        conversion_df.to_excel(writer, sheet_name='Conversion_Factors', index=False)
    
    print(f"\n✓ Saved to: {output_file}")
    
    # Statistics
    valid_scores = df['normalized_score'].dropna()
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nNormalized: {len(valid_scores)} data points")
    print(f"Mean: {valid_scores.mean():.2f}")
    print(f"Median: {valid_scores.median():.2f}")
    print(f"Std: {valid_scores.std():.2f}")
    print(f"Range: {valid_scores.min():.2f} - {valid_scores.max():.2f}")
    
    # Count zeros
    zero_count = (valid_scores == 0).sum()
    print(f"\nZero values (Not Detected): {zero_count} ({zero_count/len(valid_scores)*100:.1f}%)")
    
    print(f"\nDistribution:")
    for i in range(5):
        count = ((valid_scores >= i) & (valid_scores < i+1)).sum()
        pct = count/len(valid_scores)*100
        print(f"  {i}.0-{i+1}.0: {count:3d} ({pct:5.1f}%)")
    
    # Show distribution excluding zeros
    non_zero_scores = valid_scores[valid_scores > 0]
    if len(non_zero_scores) > 0:
        print(f"\nDistribution (excluding zeros):")
        print(f"  Count: {len(non_zero_scores)}")
        print(f"  Mean: {non_zero_scores.mean():.2f}")
        print(f"  Median: {non_zero_scores.median():.2f}")
        print(f"  Range: {non_zero_scores.min():.2f} - {non_zero_scores.max():.2f}")
    
    print("\nBy method:")
    for method in df['measurement_method'].unique():
        method_scores = df[(df['measurement_method'] == method) & 
                          (df['normalized_score'].notna())]['normalized_score']
        if len(method_scores) > 0:
            zeros = (method_scores == 0).sum()
            print(f"\n{method}:")
            print(f"  Count: {len(method_scores)}")
            print(f"  Zeros: {zeros} ({zeros/len(method_scores)*100:.1f}%)")
            print(f"  Mean: {method_scores.mean():.2f}")
            print(f"  Range: {method_scores.min():.2f} - {method_scores.max():.2f}")
    
    # Final unit verification
    print("\n" + "="*70)
    print("FINAL UNIT VERIFICATION")
    print("="*70)
    print("\nqPCR data units after processing:")
    qpcr_final = df[df['measurement_method'].str.contains('qPCR|PCR', case=False, na=False)]
    if len(qpcr_final) > 0:
        for units, count in qpcr_final['units'].value_counts().items():
            print(f"  {units}: {count}")
    
    print("\n" + "="*70)
    print("DONE!")
    print("="*70)

if __name__ == "__main__":
    main()