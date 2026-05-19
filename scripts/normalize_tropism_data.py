"""
Normalize tropism data from different measurement methods to 0-5 scale
Updated with specific measurement methods: 
Luciferase_ex_vivo, Luciferase_in_vivo, qPCR, GFP/mCherry, IHC, Western, ELISA
"""
import pandas as pd
import numpy as np
import warnings
from datetime import datetime

class TropismNormalizer:
    """
    Normalize tropism measurements to standardized 0-5 scale
    """
    
    def __init__(self):
        """Initialize normalizer with method-specific parameters"""
        
        # Define normalization parameters for each method
        self.normalization_params = {
            'qPCR': {
                'log_min': 6,      # 1e6 vg/ug DNA
                'log_max': 10,     # 1e10 vg/ug DNA
                'log_range': 4,
                'use_log': True
            },
            'Luciferase_ex_vivo': {
                'log_min': 3,      # 1e3 RLU
                'log_max': 8,      # 1e8 RLU
                'log_range': 5,
                'use_log': True
            },
            'Luciferase_in_vivo': {
                'log_min': 4,      # 1e4 photons/sec/cm²/sr
                'log_max': 8,      # 1e8 photons/sec/cm²/sr
                'log_range': 4,
                'use_log': True
            },
            'GFP/mCherry': {
                'min': 0,
                'max': 100,
                'use_log': False
            },
            'IHC': {
                'min': 0,
                'max': 100,
                'use_log': False
            },
            'Western': {
                'min': 0,
                'max': 1,
                'use_log': False
            },
            'ELISA': {
                'log_min': 2,
                'log_max': 7,
                'log_range': 5,
                'use_log': True
            }
        }
    
    def normalize_value(self, raw_value, units, method):
        """
        Normalize a single value to 0-5 scale
        
        Args:
            raw_value (float or str): Raw measurement value
            units (str): Measurement units
            method (str): Measurement method
            
        Returns:
            float: Normalized score (0-5) or np.nan if cannot normalize
        """
        
        # Handle special cases
        if pd.isna(raw_value) or raw_value == '':
            return np.nan
        
        # Handle text indicators
        if isinstance(raw_value, str):
            raw_value_lower = raw_value.lower()
            if raw_value_lower in ['nt', 'not tested', 'not measured']:
                return np.nan
            if raw_value_lower in ['bdl', 'below detection', 'nd', 'not detected']:
                return 0.0
        
        # Convert to float
        try:
            if isinstance(raw_value, str):
                value = float(raw_value)
            else:
                value = float(raw_value)
        except (ValueError, TypeError):
            warnings.warn(f"Cannot convert '{raw_value}' to float")
            return np.nan
        
        # Handle zero or negative values
        if value <= 0:
            return 0.0
        
        # Normalize based on method
        method_clean = method.strip().lower() if isinstance(method, str) else ''
        
        # qPCR normalization
        if 'qpcr' in method_clean or method_clean == 'pcr':
            return self._normalize_qpcr(value, units)
        
        # Luciferase ex vivo normalization
        elif 'luciferase_ex_vivo' in method_clean or 'ex_vivo' in method_clean:
            return self._normalize_luciferase_ex_vivo(value, units)
        
        # Luciferase in vivo normalization (BLI)
        elif 'luciferase_in_vivo' in method_clean or 'in_vivo' in method_clean:
            return self._normalize_luciferase_in_vivo(value, units)
        
        # Generic luciferase (default to ex vivo)
        elif 'luciferase' in method_clean or 'luc' in method_clean:
            # Check units to determine which type
            if 'photon' in str(units).lower():
                return self._normalize_luciferase_in_vivo(value, units)
            else:
                return self._normalize_luciferase_ex_vivo(value, units)
        
        # GFP/mCherry normalization
        elif 'gfp' in method_clean or 'mcherry' in method_clean or 'fluorescence' in method_clean:
            return self._normalize_percentage(value, units)
        
        # IHC normalization
        elif 'ihc' in method_clean or 'immunohistochemistry' in method_clean:
            return self._normalize_ihc(value, units)
        
        # Western blot normalization
        elif 'western' in method_clean or 'wb' in method_clean:
            return self._normalize_western(value, units)
        
        # ELISA normalization
        elif 'elisa' in method_clean:
            return self._normalize_elisa(value, units)
        
        # Semi-quantitative (0-4 scale)
        elif 'semi' in method_clean:
            return self._normalize_semiquant(value)
        
        # Default: assume log-scale data
        else:
            warnings.warn(f"Unknown method '{method}', using default normalization")
            return self._normalize_default(value)
    
    def _normalize_qpcr(self, value, units):
        """Normalize qPCR data (vg/ug DNA or vg/diploid genome)"""
        
        log_value = np.log10(value)
        
        # Standard range: 1e6 to 1e10 vg/ug DNA
        normalized = (log_value - 6) / 4 * 5
        
        # Clip to 0-5 range
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_luciferase_ex_vivo(self, value, units):
        """Normalize ex vivo luciferase data (RLU or RLU/mg protein)"""
        
        log_value = np.log10(value)
        
        # Standard range: 1e3 to 1e8 RLU
        normalized = (log_value - 3) / 5 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_luciferase_in_vivo(self, value, units):
        """Normalize in vivo bioluminescence imaging (photons/sec/cm²/sr)"""
        
        log_value = np.log10(value)
        
        # Standard range: 1e4 to 1e8 photons/sec/cm²/sr
        normalized = (log_value - 4) / 4 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_percentage(self, value, units):
        """Normalize percentage data (% positive cells, % transduction)"""
        
        # If already 0-100 scale
        if value <= 100:
            normalized = (value / 100) * 5
        else:
            # Might be absolute count, use log scale
            log_value = np.log10(value)
            normalized = (log_value - 3) / 5 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_ihc(self, value, units):
        """Normalize IHC data (semi-quantitative or %)"""
        
        # Check if already on 0-4 or 0-5 scale
        if value <= 5:
            # Already on 0-4 or 0-5 scale
            if value <= 4:
                normalized = value * 1.25  # Convert 0-4 to 0-5
            else:
                normalized = value  # Already 0-5
        elif value <= 100:
            # Percentage
            normalized = (value / 100) * 5
        else:
            # Absolute count
            log_value = np.log10(value)
            normalized = (log_value - 3) / 5 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_western(self, value, units):
        """Normalize Western blot data (relative intensity)"""
        
        # Usually relative to control (0-1 or 0-100)
        if value <= 1:
            # 0-1 scale
            normalized = value * 5
        elif value <= 100:
            # 0-100 scale
            normalized = (value / 100) * 5
        else:
            # Absolute values
            log_value = np.log10(value)
            normalized = (log_value - 3) / 5 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_elisa(self, value, units):
        """Normalize ELISA data (ng/mL or pg/mL)"""
        
        log_value = np.log10(value)
        
        # Standard range: 1e2 to 1e7
        normalized = (log_value - 2) / 5 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_semiquant(self, value):
        """Normalize semi-quantitative scores (0-4 scale)"""
        
        # Convert 0-4 to 0-5
        normalized = value * 1.25
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def _normalize_default(self, value):
        """Default normalization for unknown methods"""
        
        # Assume log-scale data
        log_value = np.log10(value)
        
        # Use conservative range
        normalized = (log_value - 6) / 4 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        return round(normalized, 2)
    
    def normalize_dataframe(self, df):
        """
        Normalize all rows in a DataFrame
        
        Args:
            df (DataFrame): Data with raw_value, units, measurement_method columns
            
        Returns:
            DataFrame: Data with normalized_score column added/updated
        """
        
        print("Normalizing data...")
        
        # Create normalized_score column if it doesn't exist
        if 'normalized_score' not in df.columns:
            df['normalized_score'] = np.nan
        
        # Normalize each row
        normalized_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            # Skip if already normalized
            if pd.notna(row['normalized_score']):
                continue
            
            # Normalize
            normalized = self.normalize_value(
                row['raw_value'],
                row['units'],
                row['measurement_method']
            )
            
            df.at[idx, 'normalized_score'] = normalized
            
            if pd.notna(normalized):
                normalized_count += 1
            else:
                skipped_count += 1
        
        # Report results
        print(f"✓ Normalized {normalized_count} data points")
        if skipped_count > 0:
            print(f"⚠ Skipped {skipped_count} data points (missing or invalid values)")
        
        # Check for issues
        valid_scores = df['normalized_score'].dropna()
        if len(valid_scores) > 0:
            out_of_range = df[(df['normalized_score'] < 0) | (df['normalized_score'] > 5)]
            if len(out_of_range) > 0:
                print(f"⚠ Warning: {len(out_of_range)} values out of range (0-5)")
        
        return df
    
    def get_normalization_reference(self):
        """
        Get quick reference table for normalization
        
        Returns:
            DataFrame: Reference table
        """
        
        reference_data = []
        
        # qPCR examples
        for value in [1e6, 1e7, 1e8, 1e9, 1e10]:
            normalized = self.normalize_value(value, 'vg/ug DNA', 'qPCR')
            reference_data.append({
                'Method': 'qPCR',
                'Raw_Value': f'{value:.0e}',
                'Units': 'vg/ug DNA',
                'Normalized_Score': normalized
            })
        
        # Luciferase ex vivo examples
        for value in [1e3, 1e4, 1e5, 1e6, 1e7, 1e8]:
            normalized = self.normalize_value(value, 'RLU', 'Luciferase_ex_vivo')
            reference_data.append({
                'Method': 'Luciferase_ex_vivo',
                'Raw_Value': f'{value:.0e}',
                'Units': 'RLU',
                'Normalized_Score': normalized
            })
        
        # Luciferase in vivo examples
        for value in [1e4, 1e5, 1e6, 1e7, 1e8]:
            normalized = self.normalize_value(value, 'photons/sec/cm²/sr', 'Luciferase_in_vivo')
            reference_data.append({
                'Method': 'Luciferase_in_vivo',
                'Raw_Value': f'{value:.0e}',
                'Units': 'photons/sec/cm²/sr',
                'Normalized_Score': normalized
            })
        
        # GFP/mCherry examples
        for value in [0, 20, 40, 60, 80, 100]:
            normalized = self.normalize_value(value, '%', 'GFP/mCherry')
            reference_data.append({
                'Method': 'GFP/mCherry',
                'Raw_Value': str(value),
                'Units': '%',
                'Normalized_Score': normalized
            })
        
        return pd.DataFrame(reference_data)

# Standalone functions for quick use
def normalize_qpcr(raw_value):
    """Quick qPCR normalization"""
    if raw_value <= 0:
        return 0.0
    log_value = np.log10(raw_value)
    normalized = (log_value - 6) / 4 * 5
    return round(np.clip(normalized, 0, 5), 2)

def normalize_luciferase_ex_vivo(raw_value):
    """Quick ex vivo Luciferase normalization"""
    if raw_value <= 0:
        return 0.0
    log_value = np.log10(raw_value)
    normalized = (log_value - 3) / 5 * 5
    return round(np.clip(normalized, 0, 5), 2)

def normalize_luciferase_in_vivo(raw_value):
    """Quick in vivo BLI normalization"""
    if raw_value <= 0:
        return 0.0
    log_value = np.log10(raw_value)
    normalized = (log_value - 4) / 4 * 5
    return round(np.clip(normalized, 0, 5), 2)

def normalize_percentage(raw_value):
    """Quick percentage normalization"""
    if raw_value < 0:
        return 0.0
    if raw_value <= 100:
        normalized = (raw_value / 100) * 5
    else:
        log_value = np.log10(raw_value)
        normalized = (log_value - 3) / 5 * 5
    return round(np.clip(normalized, 0, 5), 2)

def normalize_semiquant(raw_value):
    """Quick semi-quantitative normalization (0-4 scale)"""
    normalized = raw_value * 1.25
    return round(np.clip(normalized, 0, 5), 2)

# Main execution
def main():
    """
    Main normalization pipeline
    """
    
    print("="*70)
    print("AAV TROPISM DATA NORMALIZATION")
    print("="*70)
    
    # Initialize normalizer
    normalizer = TropismNormalizer()
    
    # Display reference table
    print("\n" + "="*70)
    print("NORMALIZATION REFERENCE TABLE")
    print("="*70)
    
    ref_table = normalizer.get_normalization_reference()
    print("\n" + ref_table.to_string(index=False))
    
    # Load data
    print("\n" + "="*70)
    print("LOADING DATA")
    print("="*70)
    
    try:
        df = pd.read_excel('data/metadata/tropism_extraction_template_enhanced.xlsx', sheet_name='Data')
        print(f"✓ Loaded {len(df)} data points")
    except FileNotFoundError:
        print("⚠ Template file not found. Please check the file path.")
        return
    
    # Show data before normalization
    print("\nData before normalization (first 5 rows):")
    display_cols = ['serotype', 'tissue', 'measurement_method', 'raw_value', 'normalized_score']
    available_cols = [col for col in display_cols if col in df.columns]
    print(df[available_cols].head())
    
    # Normalize
    print("\n" + "="*70)
    print("NORMALIZING DATA")
    print("="*70)
    
    df = normalizer.normalize_dataframe(df)
    
    # Show data after normalization
    print("\nData after normalization (first 5 rows):")
    print(df[available_cols].head())
    
    # Statistics
    print("\n" + "="*70)
    print("NORMALIZATION STATISTICS")
    print("="*70)
    
    valid_scores = df['normalized_score'].dropna()
    
    if len(valid_scores) > 0:
        print(f"\nNormalized score statistics:")
        print(f"  Count: {len(valid_scores)}")
        print(f"  Mean: {valid_scores.mean():.2f}")
        print(f"  Median: {valid_scores.median():.2f}")
        print(f"  Std: {valid_scores.std():.2f}")
        print(f"  Min: {valid_scores.min():.2f}")
        print(f"  Max: {valid_scores.max():.2f}")
        
        # Method breakdown
        print(f"\nNormalization by method:")
        method_stats = df.groupby('measurement_method')['normalized_score'].agg(['count', 'mean', 'std'])
        print(method_stats)
    else:
        print("\n⚠ No valid normalized scores generated")
    
    # Save normalized data
    output_file = 'data/processed/tropism_data_normalized.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved normalized data to: {output_file}")
    
    # Also save back to Excel
    try:
        output_excel = 'data/processed/tropism_data_normalized.xlsx'
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data_Normalized', index=False)
            
            # Add summary sheet
            if len(valid_scores) > 0:
                summary = pd.DataFrame({
                    'Metric': [
                        'Total data points',
                        'Normalized data points',
                        'Mean normalized score',
                        'Median normalized score',
                        'Std normalized score',
                        'Min normalized score',
                        'Max normalized score',
                        'Unique papers',
                        'Unique serotypes',
                        'Unique tissues',
                        'Processing date'
                    ],
                    'Value': [
                        len(df),
                        len(valid_scores),
                        f"{valid_scores.mean():.2f}",
                        f"{valid_scores.median():.2f}",
                        f"{valid_scores.std():.2f}",
                        f"{valid_scores.min():.2f}",
                        f"{valid_scores.max():.2f}",
                        df['pmid'].nunique() if 'pmid' in df.columns else 'N/A',
                        df['serotype'].nunique() if 'serotype' in df.columns else 'N/A',
                        df['tissue'].nunique() if 'tissue' in df.columns else 'N/A',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                })
                summary.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"✓ Saved Excel file with summary: {output_excel}")
    except Exception as e:
        print(f"⚠ Could not save Excel file: {e}")
    
    print("\n" + "="*70)
    print("NORMALIZATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()