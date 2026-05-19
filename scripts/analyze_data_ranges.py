"""
Analyze actual data ranges to optimize normalization parameters
Run this AFTER extracting data but BEFORE final normalization
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data_ranges(input_file='data/metadata/tropism_extraction_template_enhanced.xlsx'):
    """
    Analyze raw value distributions by measurement method
    
    Args:
        input_file (str): Path to extraction template
    """
    
    print("="*70)
    print("DATA RANGE ANALYSIS FOR NORMALIZATION OPTIMIZATION")
    print("="*70)
    
    # Load data
    try:
        df = pd.read_excel(input_file, sheet_name='Data')
        print(f"\n✓ Loaded {len(df)} data points")
    except FileNotFoundError:
        print(f"✗ Error: File not found: {input_file}")
        return None
    
    # Filter to valid numeric data
    df_valid = df[df['raw_value'].notna()].copy()
    
    # Convert raw_value to numeric (handle strings)
    def safe_float_convert(val):
        if pd.isna(val):
            return np.nan
        if isinstance(val, str):
            val_lower = val.lower()
            if val_lower in ['nt', 'not tested', 'bdl', 'nd']:
                return np.nan
        try:
            return float(val)
        except:
            return np.nan
    
    df_valid['raw_value_numeric'] = df_valid['raw_value'].apply(safe_float_convert)
    df_valid = df_valid[df_valid['raw_value_numeric'].notna()]
    df_valid = df_valid[df_valid['raw_value_numeric'] > 0]  # Remove zeros for log
    
    print(f"✓ Valid numeric data points: {len(df_valid)}")
    
    # Group by measurement method
    methods = df_valid['measurement_method'].unique()
    
    print("\n" + "="*70)
    print("RECOMMENDED NORMALIZATION PARAMETERS")
    print("="*70)
    
    recommendations = {}
    
    for method in methods:
        method_data = df_valid[df_valid['measurement_method'] == method]['raw_value_numeric']
        
        if len(method_data) == 0:
            continue
        
        print(f"\n{method}:")
        print(f"  Data points: {len(method_data)}")
        print(f"  Range: {method_data.min():.2e} to {method_data.max():.2e}")
        
        # Calculate log values
        log_values = np.log10(method_data)
        
        print(f"  Log10 range: {log_values.min():.2f} to {log_values.max():.2f}")
        print(f"  Log10 mean: {log_values.mean():.2f}")
        print(f"  Log10 median: {log_values.median():.2f}")
        print(f"  Log10 std: {log_values.std():.2f}")
        
        # Calculate percentiles
        p5 = np.percentile(log_values, 5)
        p95 = np.percentile(log_values, 95)
        
        print(f"  5th percentile (log10): {p5:.2f}")
        print(f"  95th percentile (log10): {p95:.2f}")
        
        # Recommend parameters
        # Use 5th and 95th percentiles to avoid outliers
        recommended_min = np.floor(p5)
        recommended_max = np.ceil(p95)
        recommended_range = recommended_max - recommended_min
        
        print(f"\n  RECOMMENDED PARAMETERS:")
        print(f"    log_min: {int(recommended_min)}")
        print(f"    log_max: {int(recommended_max)}")
        print(f"    log_range: {int(recommended_range)}")
        
        recommendations[method] = {
            'log_min': int(recommended_min),
            'log_max': int(recommended_max),
            'log_range': int(recommended_range),
            'n_points': len(method_data),
            'actual_min': method_data.min(),
            'actual_max': method_data.max()
        }
        
        # Check if current defaults are appropriate
        current_defaults = {
            'qPCR': {'log_min': 6, 'log_max': 10},
            'Luciferase_ex_vivo': {'log_min': 3, 'log_max': 8},
            'Luciferase_in_vivo': {'log_min': 4, 'log_max': 8},
        }
        
        method_key = method.replace('/', '_').lower()
        for key in current_defaults:
            if key.lower() in method_key:
                current = current_defaults[key]
                if recommended_min < current['log_min'] or recommended_max > current['log_max']:
                    print(f"  ⚠️  WARNING: Your data exceeds current defaults!")
                    print(f"      Current: {current['log_min']} to {current['log_max']}")
                    print(f"      Recommended: {int(recommended_min)} to {int(recommended_max)}")
                else:
                    print(f"  ✓ Current defaults are appropriate")
                break
    
    # Visualize distributions
    print("\n" + "="*70)
    print("GENERATING DISTRIBUTION PLOTS")
    print("="*70)
    
    n_methods = len(methods)
    fig, axes = plt.subplots(n_methods, 2, figsize=(14, 4*n_methods))
    
    if n_methods == 1:
        axes = axes.reshape(1, -1)
    
    for idx, method in enumerate(methods):
        method_data = df_valid[df_valid['measurement_method'] == method]['raw_value_numeric']
        
        if len(method_data) == 0:
            continue
        
        # Plot 1: Raw value distribution (log scale)
        ax1 = axes[idx, 0]
        ax1.hist(method_data, bins=30, edgecolor='black', alpha=0.7)
        ax1.set_xscale('log')
        ax1.set_xlabel('Raw Value')
        ax1.set_ylabel('Frequency')
        ax1.set_title(f'{method} - Raw Value Distribution')
        ax1.grid(alpha=0.3)
        
        # Add vertical lines for min/max
        ax1.axvline(method_data.min(), color='red', linestyle='--', 
                   label=f'Min: {method_data.min():.2e}')
        ax1.axvline(method_data.max(), color='red', linestyle='--', 
                   label=f'Max: {method_data.max():.2e}')
        ax1.legend()
        
        # Plot 2: Log10 distribution
        ax2 = axes[idx, 1]
        log_values = np.log10(method_data)
        ax2.hist(log_values, bins=30, edgecolor='black', alpha=0.7, color='coral')
        ax2.set_xlabel('Log10(Raw Value)')
        ax2.set_ylabel('Frequency')
        ax2.set_title(f'{method} - Log10 Distribution')
        ax2.grid(alpha=0.3)
        
        # Add vertical lines for recommended range
        if method in recommendations:
            rec = recommendations[method]
            ax2.axvline(rec['log_min'], color='green', linestyle='--', 
                       label=f"Recommended min: {rec['log_min']}")
            ax2.axvline(rec['log_max'], color='green', linestyle='--', 
                       label=f"Recommended max: {rec['log_max']}")
            ax2.legend()
    
    plt.tight_layout()
    output_plot = 'results/figures/data_range_analysis.png'
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved distribution plots: {output_plot}")
    
    # Generate Python code for updated parameters
    print("\n" + "="*70)
    print("COPY THIS CODE TO UPDATE YOUR NORMALIZATION SCRIPT")
    print("="*70)
    
    print("\n# Updated normalization parameters based on your data:")
    print("self.normalization_params = {")
    
    for method, params in recommendations.items():
        method_key = method.replace('/', '_').replace(' ', '_')
        print(f"    '{method_key}': {{")
        print(f"        'log_min': {params['log_min']},")
        print(f"        'log_max': {params['log_max']},")
        print(f"        'log_range': {params['log_range']},")
        print(f"        'use_log': True")
        print(f"    }},")
    
    print("}")
    
    # Save recommendations to file
    output_file = 'data/metadata/normalization_parameters_recommended.txt'
    with open(output_file, 'w') as f:
        f.write("RECOMMENDED NORMALIZATION PARAMETERS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Analysis date: {pd.Timestamp.now()}\n")
        f.write(f"Total data points analyzed: {len(df_valid)}\n\n")
        
        for method, params in recommendations.items():
            f.write(f"\n{method}:\n")
            f.write(f"  Data points: {params['n_points']}\n")
            f.write(f"  Actual range: {params['actual_min']:.2e} to {params['actual_max']:.2e}\n")
            f.write(f"  Recommended log_min: {params['log_min']}\n")
            f.write(f"  Recommended log_max: {params['log_max']}\n")
            f.write(f"  Recommended log_range: {params['log_range']}\n")
    
    print(f"\n✓ Saved recommendations to: {output_file}")
    
    return recommendations

if __name__ == "__main__":
    recommendations = analyze_data_ranges()