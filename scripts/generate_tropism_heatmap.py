"""
Generate AAV tropism heatmaps from normalized data
WITH qPCR vs Luciferase distinction
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_normalized_data(filepath='data/processed/tropism_harmonised.xlsx'):
    """Load normalized tropism data"""
    
    print("="*70)
    print("LOADING DATA")
    print("="*70)
    
    try:
        df = pd.read_excel(filepath)
        print(f"✓ Loaded {len(df)} data points")
        
        # Filter to valid normalized scores
        df_valid = df[df['normalized_score'].notna()].copy()
        print(f"✓ Found {len(df_valid)} data points with normalized scores")
        
        # Show breakdown by measurement method
        print("\nData by measurement method:")
        method_counts = df_valid['measurement_method'].value_counts()
        for method, count in method_counts.items():
            pct = count / len(df_valid) * 100
            print(f"  {method}: {count} ({pct:.1f}%)")
        
        return df_valid
    
    except FileNotFoundError:
        print(f"✗ Error: Could not find {filepath}")
        return None

def create_method_specific_heatmaps(df, output_dir='results/figures'):
    """
    Create separate heatmaps for qPCR (delivery) vs Luciferase (function)
    """
    
    print("\n" + "="*70)
    print("GENERATING METHOD-SPECIFIC HEATMAPS")
    print("="*70)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Define method categories
    method_categories = {
        'qPCR_Delivery': ['qPCR', 'PCR', 'Quantitative PCR'],
        'Luciferase_Function': ['Luciferase_ex_vivo', 'Luciferase_in_vivo', 'Luciferase'],
        'GFP_Function': ['GFP/mCherry', 'GFP', 'mCherry', 'Fluorescence']
    }
    
    for category, method_list in method_categories.items():
        # Filter data
        df_method = df[df['measurement_method'].isin(method_list)]
        
        if len(df_method) == 0:
            print(f"\n  ⚠ No data for {category}, skipping")
            continue
        
        print(f"\nCreating {category} heatmap (n={len(df_method)})...")
        
        # Create pivot table
        heatmap_data = df_method.pivot_table(
            values='normalized_score',
            index='serotype',
            columns='tissue',
            aggfunc='mean'
        )
        
        if heatmap_data.empty:
            print(f"  ⚠ No valid data for {category}, skipping")
            continue
        
        # Create figure
        n_tissues = heatmap_data.shape[1]
        fig, ax = plt.subplots(figsize=(max(10, n_tissues*1.5), 7))
        
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            vmin=0,
            vmax=5,
            cbar_kws={'label': 'Tropism Score (0-5)'},
            linewidths=0.5,
            linecolor='gray',
            ax=ax
        )
        
        # Customize title based on method type
        if 'qPCR' in category:
            title = f'AAV Tropism - Vector Delivery (qPCR)\n(n={len(df_method)} data points)'
            subtitle = 'Measures: Vector genome biodistribution'
        elif 'Luciferase' in category:
            title = f'AAV Tropism - Functional Transduction (Luciferase)\n(n={len(df_method)} data points)'
            subtitle = 'Measures: Transgene expression'
        else:
            title = f'AAV Tropism - Functional Transduction (GFP)\n(n={len(df_method)} data points)'
            subtitle = 'Measures: Transgene expression'
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.text(0.5, -0.15, subtitle, transform=ax.transAxes,
                ha='center', fontsize=10, style='italic', color='gray')
        
        ax.set_xlabel('Tissue', fontsize=11, fontweight='bold')
        ax.set_ylabel('Serotype', fontsize=11, fontweight='bold')
        
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        
        output_file = f"{output_dir}/tropism_heatmap_method_{category.lower()}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        
        plt.close()

def compare_qpcr_vs_luciferase(df, output_dir='results/figures'):
    """
    Direct comparison of qPCR (delivery) vs Luciferase (function) for same tissues
    """
    
    print("\n" + "="*70)
    print("COMPARING qPCR vs LUCIFERASE")
    print("="*70)
    
    # Separate by method type
    qpcr_data = df[df['measurement_method'].str.contains('qPCR|PCR', case=False, na=False)]
    luc_data = df[df['measurement_method'].str.contains('Luciferase', case=False, na=False)]
    
    print(f"\nqPCR data: {len(qpcr_data)} points")
    print(f"Luciferase data: {len(luc_data)} points")
    
    # Find tissues with both methods
    qpcr_tissues = set(qpcr_data['tissue'].unique())
    luc_tissues = set(luc_data['tissue'].unique())
    common_tissues = qpcr_tissues & luc_tissues
    
    if not common_tissues:
        print("  ⚠ No tissues with both qPCR and Luciferase data")
        return
    
    print(f"\nTissues with both methods: {len(common_tissues)}")
    print(f"  {', '.join(sorted(common_tissues))}")
    
    # Create comparison for each tissue
    for tissue in sorted(common_tissues):
        qpcr_tissue = qpcr_data[qpcr_data['tissue'] == tissue]
        luc_tissue = luc_data[luc_data['tissue'] == tissue]
        
        # Find serotypes with both methods
        qpcr_serotypes = set(qpcr_tissue['serotype'].unique())
        luc_serotypes = set(luc_tissue['serotype'].unique())
        common_serotypes = qpcr_serotypes & luc_serotypes
        
        if len(common_serotypes) < 2:
            continue
        
        print(f"\n{tissue}: {len(common_serotypes)} serotypes with both methods")
        
        # Create comparison data
        comparison_data = pd.DataFrame({
            'qPCR (Delivery)': qpcr_tissue.groupby('serotype')['normalized_score'].mean(),
            'Luciferase (Function)': luc_tissue.groupby('serotype')['normalized_score'].mean()
        })
        
        # Calculate delivery-to-function ratio
        comparison_data['Delivery/Function Ratio'] = (
            comparison_data['qPCR (Delivery)'] / comparison_data['Luciferase (Function)']
        )
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Heatmap comparison
        sns.heatmap(
            comparison_data[['qPCR (Delivery)', 'Luciferase (Function)']],
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            vmin=0,
            vmax=5,
            cbar_kws={'label': 'Tropism Score (0-5)'},
            linewidths=0.5,
            linecolor='gray',
            ax=ax1
        )
        
        ax1.set_title(f'{tissue}\nDelivery vs Function', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Measurement Type', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Serotype', fontsize=10, fontweight='bold')
        
        # Scatter plot
        ax2.scatter(comparison_data['qPCR (Delivery)'], 
                   comparison_data['Luciferase (Function)'],
                   s=100, alpha=0.6, c='steelblue')
        
        # Add diagonal line (perfect correlation)
        ax2.plot([0, 5], [0, 5], 'r--', alpha=0.5, label='Perfect correlation')
        
        # Label points
        for idx, row in comparison_data.iterrows():
            ax2.annotate(idx, 
                        (row['qPCR (Delivery)'], row['Luciferase (Function)']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.7)
        
        ax2.set_xlabel('qPCR Score (Delivery)', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Luciferase Score (Function)', fontsize=10, fontweight='bold')
        ax2.set_title(f'{tissue}\nDelivery vs Function Correlation', 
                     fontsize=12, fontweight='bold')
        ax2.set_xlim(0, 5)
        ax2.set_ylim(0, 5)
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        # Add interpretation text
        above_line = comparison_data['Luciferase (Function)'] > comparison_data['qPCR (Delivery)']
        below_line = comparison_data['Luciferase (Function)'] < comparison_data['qPCR (Delivery)']
        
        interpretation = ""
        if above_line.sum() > 0:
            interpretation += f"Above line: High expression efficiency\n"
        if below_line.sum() > 0:
            interpretation += f"Below line: Low expression efficiency"
        
        if interpretation:
            ax2.text(0.05, 0.95, interpretation,
                    transform=ax2.transAxes, fontsize=9,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        tissue_safe = tissue.lower().replace(' ', '_')
        output_file = f"{output_dir}/qpcr_vs_luciferase_{tissue_safe}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        
        plt.close()

def create_method_comparison_summary(df, output_dir='results/figures'):
    """
    Overall summary comparing qPCR vs Luciferase across all data
    """
    
    print("\n" + "="*70)
    print("GENERATING METHOD COMPARISON SUMMARY")
    print("="*70)
    
    # Categorize methods
    def categorize_method(method):
        method_lower = str(method).lower()
        if 'qpcr' in method_lower or 'pcr' in method_lower:
            return 'qPCR (Delivery)'
        elif 'luciferase' in method_lower:
            return 'Luciferase (Function)'
        elif 'gfp' in method_lower or 'mcherry' in method_lower:
            return 'GFP (Function)'
        else:
            return 'Other'
    
    df['method_category'] = df['measurement_method'].apply(categorize_method)
    
    # Overall statistics by method
    method_stats = df.groupby('method_category')['normalized_score'].agg(['mean', 'std', 'count'])
    
    print("\nOverall tropism by measurement method:")
    print(method_stats)
    
    # By tissue and method
    tissue_method_stats = df.groupby(['tissue', 'method_category'])['normalized_score'].mean().unstack()
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar plot of overall means
    method_stats['mean'].plot(kind='bar', ax=ax1, color=['steelblue', 'coral', 'lightgreen'],
                              yerr=method_stats['std'], capsize=4)
    ax1.set_title('Average Tropism by Measurement Method', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Measurement Method', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Tropism Score (0-5)', fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 5)
    ax1.axhline(y=2.5, color='red', linestyle='--', alpha=0.5, label='Midpoint')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Heatmap of tissue × method
    if not tissue_method_stats.empty:
        sns.heatmap(
            tissue_method_stats,
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            vmin=0,
            vmax=5,
            cbar_kws={'label': 'Tropism Score (0-5)'},
            linewidths=0.5,
            linecolor='gray',
            ax=ax2
        )
        
        ax2.set_title('Tropism by Tissue and Method', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Measurement Method', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Tissue', fontsize=11, fontweight='bold')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/method_comparison_summary.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved method comparison: {output_file}")
    
    # Save statistics
    method_stats.to_csv(f"{output_dir}/tropism_by_method.csv")
    tissue_method_stats.to_csv(f"{output_dir}/tropism_by_tissue_and_method.csv")
    print(f"✓ Saved method statistics CSVs")
    
    plt.close()

def create_combined_heatmap_with_method_indicator(df, output_dir='results/figures'):
    """
    Create heatmap that shows both qPCR and Luciferase data with indicators
    """
    
    print("\n" + "="*70)
    print("GENERATING COMBINED HEATMAP WITH METHOD INDICATORS")
    print("="*70)
    
    # Create pivot tables for each method
    qpcr_data = df[df['measurement_method'].str.contains('qPCR|PCR', case=False, na=False)]
    luc_data = df[df['measurement_method'].str.contains('Luciferase', case=False, na=False)]
    
    qpcr_pivot = qpcr_data.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='tissue',
        aggfunc='mean'
    )
    
    luc_pivot = luc_data.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='tissue',
        aggfunc='mean'
    )
    
    # Combine: prefer Luciferase (functional), fall back to qPCR (delivery)
    combined = luc_pivot.combine_first(qpcr_pivot)
    
    # Create annotations showing which method
    annotations = pd.DataFrame(
        index=combined.index,
        columns=combined.columns,
        dtype=object
    )
    
    for i in range(combined.shape[0]):
        for j in range(combined.shape[1]):
            serotype = combined.index[i]
            tissue = combined.columns[j]
            
            has_luc = (serotype in luc_pivot.index and 
                      tissue in luc_pivot.columns and 
                      pd.notna(luc_pivot.loc[serotype, tissue]))
            has_qpcr = (serotype in qpcr_pivot.index and 
                       tissue in qpcr_pivot.columns and 
                       pd.notna(qpcr_pivot.loc[serotype, tissue]))
            
            if pd.notna(combined.iloc[i, j]):
                value = combined.iloc[i, j]
                if has_luc and has_qpcr:
                    annotations.iloc[i, j] = f"{value:.2f}\n(L+D)"
                elif has_luc:
                    annotations.iloc[i, j] = f"{value:.2f}\n(L)"
                elif has_qpcr:
                    annotations.iloc[i, j] = f"{value:.2f}\n(D)"
                else:
                    annotations.iloc[i, j] = f"{value:.2f}"
            else:
                annotations.iloc[i, j] = ""
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 9))
    
    sns.heatmap(
        combined,
        annot=annotations,
        fmt='',
        cmap='YlOrRd',
        vmin=0,
        vmax=5,
        cbar_kws={'label': 'Tropism Score (0-5)'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title('AAV Tropism - Combined Data\n(L)=Luciferase/Function, (D)=qPCR/Delivery, (L+D)=Both', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Tissue', fontsize=11, fontweight='bold')
    ax.set_ylabel('Serotype', fontsize=11, fontweight='bold')
    
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/tropism_heatmap_combined_with_method.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved combined heatmap: {output_file}")
    
    plt.close()

def create_tropism_heatmap(df, output_dir='results/figures'):
    """
    Create comprehensive tropism heatmap
    
    Args:
        df: DataFrame with normalized tropism data
        output_dir: Where to save figures
    """
    
    print("\n" + "="*70)
    print("GENERATING TROPISM HEATMAP")
    print("="*70)
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get unique serotypes and tissues
    serotypes = sorted(df['serotype'].unique())
    tissues = sorted(df['tissue'].unique())
    
    print(f"\nSerotypes: {len(serotypes)}")
    print(f"  {', '.join(serotypes)}")
    print(f"\nTissues: {len(tissues)}")
    print(f"  {', '.join(tissues)}")
    
    # Create pivot table (serotypes × tissues)
    heatmap_data = df.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='tissue',
        aggfunc='mean'
    )
    
    # Count data points for each cell
    count_data = df.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='tissue',
        aggfunc='count'
    )
    
    print(f"\nHeatmap dimensions: {heatmap_data.shape[0]} serotypes × {heatmap_data.shape[1]} tissues")
    print(f"Total cells: {heatmap_data.shape[0] * heatmap_data.shape[1]}")
    print(f"Filled cells: {heatmap_data.notna().sum().sum()}")
    print(f"Coverage: {heatmap_data.notna().sum().sum() / (heatmap_data.shape[0] * heatmap_data.shape[1]) * 100:.1f}%")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(
        heatmap_data,
        annot=True,           # Show values
        fmt='.2f',            # 2 decimal places
        cmap='YlOrRd',        # Yellow-Orange-Red colormap
        vmin=0,               # Minimum value
        vmax=5,               # Maximum value
        cbar_kws={'label': 'Tropism Score (0-5)'},
        linewidths=0.5,       # Grid lines
        linecolor='gray',
        ax=ax
    )
    
    # Customize
    ax.set_title('AAV Serotype Tropism Across Tissues', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Tissue', fontsize=12, fontweight='bold')
    ax.set_ylabel('Serotype', fontsize=12, fontweight='bold')
    
    # Rotate labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    
    # Save
    output_file = f"{output_dir}/tropism_heatmap_all.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved heatmap: {output_file}")
    
    plt.close()
    
    return heatmap_data, count_data

def create_heatmap_with_counts(df, output_dir='results/figures'):
    """
    Create heatmap with sample size annotations
    """
    
    print("\n" + "="*70)
    print("GENERATING HEATMAP WITH SAMPLE COUNTS")
    print("="*70)
    
    # Create pivot tables
    mean_data = df.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='tissue',
        aggfunc='mean'
    )
    
    count_data = df.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='tissue',
        aggfunc='count'
    )
    
    # Create annotations with mean ± count
    annotations = mean_data.copy()
    for i in range(annotations.shape[0]):
        for j in range(annotations.shape[1]):
            if pd.notna(annotations.iloc[i, j]):
                mean_val = annotations.iloc[i, j]
                count_val = count_data.iloc[i, j]
                annotations.iloc[i, j] = f"{mean_val:.2f}\n(n={int(count_val)})"
            else:
                annotations.iloc[i, j] = ""
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # Create heatmap
    sns.heatmap(
        mean_data,
        annot=annotations,    # Custom annotations
        fmt='',               # String format
        cmap='YlOrRd',
        vmin=0,
        vmax=5,
        cbar_kws={'label': 'Tropism Score (0-5)'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title('AAV Serotype Tropism with Sample Sizes', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Tissue', fontsize=12, fontweight='bold')
    ax.set_ylabel('Serotype', fontsize=12, fontweight='bold')
    
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/tropism_heatmap_with_counts.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved heatmap with counts: {output_file}")
    
    plt.close()

def create_tissue_specific_heatmaps(df, output_dir='results/figures'):
    """
    Create separate heatmaps for different tissue categories
    """
    
    print("\n" + "="*70)
    print("GENERATING TISSUE-SPECIFIC HEATMAPS")
    print("="*70)
    
    # Define tissue categories based on YOUR data
    tissue_categories = {}
    
    all_tissues = df['tissue'].unique()
    
    # Categorize tissues
    cns_tissues = [t for t in all_tissues if t in ['Brain', 'Spinal Cord', 'Olfactory Bulb']]
    sensory_tissues = [t for t in all_tissues if t in ['Retina', 'Cochlea', 'Olfactory Epithelium']]
    muscle_tissues = [t for t in all_tissues if t in ['Heart', 'Skeletal Muscle', 'Diaphragm']]
    visceral_tissues = [t for t in all_tissues if t in ['Liver', 'Lung', 'Kidney', 'Spleen', 'Pancreas']]
    pns_tissues = [t for t in all_tissues if t in ['Dorsal Root Ganglion', 'Peripheral Nerve', 'Enteric Nervous System']]
    
    if cns_tissues:
        tissue_categories['CNS'] = cns_tissues
    if sensory_tissues:
        tissue_categories['Sensory'] = sensory_tissues
    if muscle_tissues:
        tissue_categories['Muscle'] = muscle_tissues
    if visceral_tissues:
        tissue_categories['Visceral'] = visceral_tissues
    if pns_tissues:
        tissue_categories['PNS'] = pns_tissues
    
    # Create heatmap for each category
    for category, tissues in tissue_categories.items():
        if not tissues:
            continue
        
        print(f"\nCreating {category} heatmap...")
        
        # Filter data
        df_cat = df[df['tissue'].isin(tissues)]
        
        if len(df_cat) == 0:
            print(f"  ⚠ No data for {category}, skipping")
            continue
        
        # Create pivot table
        heatmap_data = df_cat.pivot_table(
            values='normalized_score',
            index='serotype',
            columns='tissue',
            aggfunc='mean'
        )
        
        # Create figure
        fig, ax = plt.subplots(figsize=(max(8, len(tissues)*1.5), 6))
        
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            vmin=0,
            vmax=5,
            cbar_kws={'label': 'Tropism Score (0-5)'},
            linewidths=0.5,
            linecolor='gray',
            ax=ax
        )
        
        ax.set_title(f'AAV Tropism - {category} Tissues', 
                     fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Tissue', fontsize=11, fontweight='bold')
        ax.set_ylabel('Serotype', fontsize=11, fontweight='bold')
        
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        
        output_file = f"{output_dir}/tropism_heatmap_{category.lower()}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        
        plt.close()

def create_summary_statistics(df, output_dir='results/figures'):
    """
    Create summary statistics and bar plots
    """
    
    print("\n" + "="*70)
    print("GENERATING SUMMARY STATISTICS")
    print("="*70)
    
    # By serotype
    serotype_stats = df.groupby('serotype')['normalized_score'].agg(['mean', 'std', 'count'])
    serotype_stats = serotype_stats.sort_values('mean', ascending=False)
    
    print("\nTropism by Serotype (overall):")
    print(serotype_stats)
    
    # By tissue
    tissue_stats = df.groupby('tissue')['normalized_score'].agg(['mean', 'std', 'count'])
    tissue_stats = tissue_stats.sort_values('mean', ascending=False)
    
    print("\nTropism by Tissue (overall):")
    print(tissue_stats)
    
    # Create bar plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Serotype plot
    serotype_stats['mean'].plot(kind='bar', ax=ax1, color='steelblue', 
                                 yerr=serotype_stats['std'], capsize=4)
    ax1.set_title('Average Tropism by Serotype', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Serotype', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Tropism Score (0-5)', fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 5)
    ax1.axhline(y=2.5, color='red', linestyle='--', alpha=0.5, label='Midpoint')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Tissue plot
    tissue_stats['mean'].plot(kind='barh', ax=ax2, color='coral')
    ax2.set_title('Average Tropism by Tissue', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Tropism Score (0-5)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Tissue', fontsize=11, fontweight='bold')
    ax2.set_xlim(0, 5)
    ax2.axvline(x=2.5, color='red', linestyle='--', alpha=0.5, label='Midpoint')
    ax2.legend()
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/tropism_summary_bars.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved summary plots: {output_file}")
    
    plt.close()
    
    # Save statistics to CSV
    serotype_stats.to_csv(f"{output_dir}/tropism_by_serotype.csv")
    tissue_stats.to_csv(f"{output_dir}/tropism_by_tissue.csv")
    print(f"✓ Saved statistics CSVs")

def create_data_coverage_plot(df, output_dir='results/figures'):
    """
    Visualize data coverage (which serotype-tissue combinations have data)
    """
    
    print("\n" + "="*70)
    print("GENERATING DATA COVERAGE PLOT")
    print("="*70)
    
    # Create binary matrix (1 = have data, 0 = no data)
    coverage = df.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='tissue',
        aggfunc='count'
    )
    
    # Convert to binary
    coverage_binary = coverage.notna().astype(int)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(
        coverage_binary,
        cmap='RdYlGn',
        cbar_kws={'label': 'Data Available', 'ticks': [0, 1]},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title('Data Coverage: Serotype × Tissue Combinations', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Tissue', fontsize=12, fontweight='bold')
    ax.set_ylabel('Serotype', fontsize=12, fontweight='bold')
    
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    # Add coverage statistics
    total_cells = coverage_binary.shape[0] * coverage_binary.shape[1]
    filled_cells = coverage_binary.sum().sum()
    coverage_pct = filled_cells / total_cells * 100
    
    ax.text(0.02, 0.98, f'Coverage: {filled_cells}/{total_cells} ({coverage_pct:.1f}%)',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/data_coverage.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved coverage plot: {output_file}")
    
    plt.close()

def create_route_specific_heatmaps(df, output_dir='results/figures'):
    """
    Create separate heatmaps for different administration routes
    """
    
    print("\n" + "="*70)
    print("GENERATING ROUTE-SPECIFIC HEATMAPS")
    print("="*70)
    
    # Check what routes you have
    routes = df['administration_route'].unique()
    print(f"\nAdministration routes in data: {len(routes)}")
    for route in routes:
        count = len(df[df['administration_route'] == route])
        print(f"  {route}: {count} data points")
    
    # Define route categories
    route_categories = {
        'Systemic_IV': ['IV', 'Intravenous', 'Tail vein', 'Retro-orbital', 'Facial vein'],
        'Intramuscular': ['IM', 'Intramuscular', 'Direct muscle injection'],
        'CNS_Local': ['Intrathecal', 'IT', 'Intracerebroventricular', 'ICV', 
                      'Intracranial', 'Cisterna magna'],
        'Cardiac_Local': ['Intracoronary', 'Intramyocardial', 'Intrapericardial'],
        'Respiratory': ['Intranasal', 'IN', 'Intratracheal', 'Aerosol'],
        'Sensory_Local': ['Subretinal', 'Intravitreal', 'Round window injection']
    }
    
    # Create heatmap for each route category
    for category, route_list in route_categories.items():
        # Filter data for this route category
        df_route = df[df['administration_route'].isin(route_list)]
        
        if len(df_route) == 0:
            print(f"\n  ⚠ No data for {category}, skipping")
            continue
        
        print(f"\nCreating {category} heatmap (n={len(df_route)})...")
        
        # Create pivot table
        heatmap_data = df_route.pivot_table(
            values='normalized_score',
            index='serotype',
            columns='tissue',
            aggfunc='mean'
        )
        
        # Skip if no data
        if heatmap_data.empty:
            print(f"  ⚠ No valid data for {category}, skipping")
            continue
        
        # Create figure
        n_tissues = heatmap_data.shape[1]
        fig, ax = plt.subplots(figsize=(max(10, n_tissues*1.5), 7))
        
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            vmin=0,
            vmax=5,
            cbar_kws={'label': 'Tropism Score (0-5)'},
            linewidths=0.5,
            linecolor='gray',
            ax=ax
        )
        
        # Format route name for title
        route_name = category.replace('_', ' ')
        ax.set_title(f'AAV Tropism - {route_name} Administration\n(n={len(df_route)} data points)', 
                     fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Tissue', fontsize=11, fontweight='bold')
        ax.set_ylabel('Serotype', fontsize=11, fontweight='bold')
        
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        
        output_file = f"{output_dir}/tropism_heatmap_route_{category.lower()}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        
        plt.close()

def compare_routes_for_tissue(df, tissue, output_dir='results/figures'):
    """
    Compare different administration routes for a specific tissue
    
    Args:
        df: DataFrame with data
        tissue: Tissue name to analyze
        output_dir: Output directory
    """
    
    # Filter to this tissue
    df_tissue = df[df['tissue'] == tissue].copy()
    
    if len(df_tissue) == 0:
        return
    
    print(f"\nComparing routes for {tissue}...")
    
    # Group routes
    route_categories = {
        'Systemic (IV)': ['IV', 'Intravenous', 'Tail vein', 'Retro-orbital', 'Facial vein'],
        'Local': ['Intramuscular', 'IM', 'Intrathecal', 'IT', 'Intracoronary', 
                  'Intramyocardial', 'Subretinal', 'Intravitreal', 'Round window injection']
    }
    
    # Categorize routes
    def categorize_route(route):
        for category, routes in route_categories.items():
            if route in routes:
                return category
        return 'Other'
    
    df_tissue['route_category'] = df_tissue['administration_route'].apply(categorize_route)
    
    # Create pivot table
    heatmap_data = df_tissue.pivot_table(
        values='normalized_score',
        index='serotype',
        columns='route_category',
        aggfunc='mean'
    )
    
    if heatmap_data.empty or heatmap_data.shape[1] < 2:
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        vmin=0,
        vmax=5,
        cbar_kws={'label': 'Tropism Score (0-5)'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title(f'Route Comparison - {tissue}', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Administration Route', fontsize=11, fontweight='bold')
    ax.set_ylabel('Serotype', fontsize=11, fontweight='bold')
    
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/route_comparison_{tissue.lower().replace(' ', '_')}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    
    plt.close()

def create_route_comparison_summary(df, output_dir='results/figures'):
    """
    Create summary comparing systemic vs local delivery across all tissues
    """
    
    print("\n" + "="*70)
    print("GENERATING ROUTE COMPARISON SUMMARY")
    print("="*70)
    
    # Categorize routes
    systemic_routes = ['IV', 'Intravenous', 'Tail vein', 'Retro-orbital', 'Facial vein']
    
    df['route_type'] = df['administration_route'].apply(
        lambda x: 'Systemic (IV)' if x in systemic_routes else 'Local Delivery'
    )
    
    # Get tissues that have both route types
    tissues_with_both = []
    for tissue in df['tissue'].unique():
        tissue_data = df[df['tissue'] == tissue]
        route_types = tissue_data['route_type'].unique()
        if len(route_types) > 1:
            tissues_with_both.append(tissue)
    
    if not tissues_with_both:
        print("  ⚠ No tissues with both systemic and local delivery data")
        return
    
    print(f"\nTissues with both route types: {len(tissues_with_both)}")
    print(f"  {', '.join(tissues_with_both)}")
    
    # Filter to tissues with both
    df_comparison = df[df['tissue'].isin(tissues_with_both)]
    
    # Create comparison pivot table
    comparison_data = df_comparison.pivot_table(
        values='normalized_score',
        index='tissue',
        columns='route_type',
        aggfunc='mean'
    )
    
    # Calculate fold-change
    if 'Systemic (IV)' in comparison_data.columns and 'Local Delivery' in comparison_data.columns:
        comparison_data['Fold Enhancement'] = (
            comparison_data['Local Delivery'] / comparison_data['Systemic (IV)']
        )
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Heatmap
    sns.heatmap(
        comparison_data[['Systemic (IV)', 'Local Delivery']],
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        vmin=0,
        vmax=5,
        cbar_kws={'label': 'Tropism Score (0-5)'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax1
    )
    
    ax1.set_title('Systemic vs Local Delivery', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Administration Route', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Tissue', fontsize=11, fontweight='bold')
    
    # Bar plot of fold-enhancement
    if 'Fold Enhancement' in comparison_data.columns:
        comparison_data['Fold Enhancement'].plot(kind='barh', ax=ax2, color='steelblue')
        ax2.axvline(x=1, color='red', linestyle='--', alpha=0.5, label='No difference')
        ax2.set_xlabel('Fold Enhancement (Local / Systemic)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Tissue', fontsize=11, fontweight='bold')
        ax2.set_title('Local Delivery Enhancement', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/route_comparison_summary.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved route comparison: {output_file}")
    
    # Save statistics
    comparison_data.to_csv(f"{output_dir}/route_comparison_statistics.csv")
    print(f"✓ Saved route statistics CSV")
    
    plt.close()

def analyze_routes_by_tissue(df, output_dir='results/figures'):
    """
    Analyze and compare routes for each tissue that has multiple routes
    """
    
    print("\n" + "="*70)
    print("ANALYZING ROUTES BY TISSUE")
    print("="*70)
    
    # For each tissue, check if multiple routes exist
    tissues_to_compare = []
    
    for tissue in df['tissue'].unique():
        tissue_data = df[df['tissue'] == tissue]
        n_routes = tissue_data['administration_route'].nunique()
        
        if n_routes > 1:
            tissues_to_compare.append(tissue)
            print(f"\n{tissue}: {n_routes} different routes")
            route_counts = tissue_data['administration_route'].value_counts()
            for route, count in route_counts.items():
                print(f"  {route}: {count} data points")
    
    # Create comparison plots for tissues with multiple routes
    for tissue in tissues_to_compare:
        compare_routes_for_tissue(df, tissue, output_dir)

def get_tissue_specific_local_routes():
    """Define which local routes are appropriate for each tissue"""
    return {
        'Brain': ['Intrathecal', 'IT', 'Intracerebroventricular', 'ICV', 
                  'Intracranial', 'Cisterna magna', 'Intraparenchymal'],
        'Spinal Cord': ['Intrathecal', 'IT', 'Lumbar puncture'],
        'Heart': ['Intracoronary', 'Intramyocardial', 'Intrapericardial'],
        'Skeletal Muscle': ['Intramuscular', 'IM', 'Direct muscle injection'],
        'Diaphragm': ['Intramuscular', 'IM', 'Direct muscle injection'],
        'Retina': ['Subretinal', 'Intravitreal'],
        'Cochlea': ['Round window injection', 'Cochlear injection'],
        'Lung': ['Intranasal', 'IN', 'Intratracheal', 'Aerosol', 'Intrapulmonary'],
        'Liver': [],  # No tissue-specific local routes
        'Kidney': [],
        'Spleen': [],
        'Pancreas': [],
        'Testes': []
    }

def get_systemic_routes():
    """Define systemic administration routes"""
    return ['IV', 'Intravenous', 'Tail vein', 'Retro-orbital', 'Facial vein']

def create_route_comparison_summary(df, output_dir='results/figures'):
    """
    Create summary comparing systemic vs TISSUE-MATCHED local delivery
    """
    
    print("\n" + "="*70)
    print("GENERATING TISSUE-MATCHED ROUTE COMPARISON")
    print("="*70)
    
    tissue_routes = get_tissue_specific_local_routes()
    systemic_routes = get_systemic_routes()
    
    comparison_results = []
    
    for tissue in sorted(df['tissue'].unique()):
        tissue_data = df[df['tissue'] == tissue]
        
        # Get tissue-specific local routes
        local_routes = tissue_routes.get(tissue, [])
        
        if not local_routes:
            # Skip tissues with no tissue-specific local routes
            continue
        
        # Separate systemic and tissue-matched local
        systemic_data = tissue_data[tissue_data['administration_route'].isin(systemic_routes)]
        local_data = tissue_data[tissue_data['administration_route'].isin(local_routes)]
        
        if len(systemic_data) == 0 or len(local_data) == 0:
            continue
        
        print(f"\n{tissue}:")
        print(f"  Systemic routes: {list(systemic_data['administration_route'].unique())}")
        print(f"  Local routes (tissue-matched): {list(local_data['administration_route'].unique())}")
        print(f"  Systemic n={len(systemic_data)}, Local n={len(local_data)}")
        
        systemic_mean = systemic_data['normalized_score'].mean()
        local_mean = local_data['normalized_score'].mean()
        fold_change = local_mean / systemic_mean if systemic_mean > 0 else np.nan
        
        comparison_results.append({
            'Tissue': tissue,
            'Systemic_Score': systemic_mean,
            'Local_Score': local_mean,
            'Fold_Enhancement': fold_change,
            'Systemic_n': len(systemic_data),
            'Local_n': len(local_data),
            'Local_Routes': ', '.join(local_routes[:2])  # Show first 2
        })
    
    if not comparison_results:
        print("  ⚠ No tissues with matched systemic and local data")
        return
    
    comparison_df = pd.DataFrame(comparison_results)
    
    print(f"\nTissues with tissue-matched route data: {len(comparison_df)}")
    print(f"  {', '.join(comparison_df['Tissue'].tolist())}")
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Heatmap
    heatmap_data = comparison_df.set_index('Tissue')[['Systemic_Score', 'Local_Score']]
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        vmin=0,
        vmax=5,
        cbar_kws={'label': 'Tropism Score (0-5)'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax1
    )
    
    ax1.set_title('Systemic vs Tissue-Matched Local Delivery', 
                 fontsize=14, fontweight='bold')
    ax1.set_xlabel('Delivery Route', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Tissue', fontsize=11, fontweight='bold')
    
    # Bar plot
    comparison_df.set_index('Tissue')['Fold_Enhancement'].plot(
        kind='barh', ax=ax2, color='steelblue'
    )
    ax2.axvline(x=1, color='red', linestyle='--', alpha=0.5, label='No difference')
    ax2.set_xlabel('Fold Enhancement\n(Tissue-Matched Local / Systemic)', 
                  fontsize=11, fontweight='bold')
    ax2.set_ylabel('Tissue', fontsize=11, fontweight='bold')
    ax2.set_title('Local Delivery Enhancement\n(Tissue-Specific Routes Only)', 
                 fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(axis='x', alpha=0.3)
    
    # Add note about tissue-matching
    fig.text(0.5, 0.02, 
            'Note: Local routes are tissue-specific (e.g., Intracoronary only for Heart)', 
            ha='center', fontsize=9, style='italic', color='gray')
    
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    
    output_file = f"{output_dir}/route_comparison_tissue_matched.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved route comparison: {output_file}")
    
    # Save with route information
    comparison_df.to_csv(f"{output_dir}/route_comparison_tissue_matched.csv", index=False)
    print(f"✓ Saved route statistics CSV")
    
    plt.close()

def analyze_routes_by_tissue(df, output_dir='results/figures'):
    """
    Analyze and compare TISSUE-MATCHED routes for each tissue
    """
    
    print("\n" + "="*70)
    print("ANALYZING TISSUE-MATCHED ROUTES BY TISSUE")
    print("="*70)
    
    tissue_routes = get_tissue_specific_local_routes()
    systemic_routes = get_systemic_routes()
    
    for tissue in sorted(df['tissue'].unique()):
        tissue_data = df[df['tissue'] == tissue]
        
        # Get tissue-specific local routes
        local_routes = tissue_routes.get(tissue, [])
        
        if not local_routes:
            continue
        
        # Check if we have both systemic and tissue-matched local
        systemic_data = tissue_data[tissue_data['administration_route'].isin(systemic_routes)]
        local_data = tissue_data[tissue_data['administration_route'].isin(local_routes)]
        
        if len(systemic_data) == 0 or len(local_data) == 0:
            continue
        
        print(f"\n{tissue}:")
        print(f"  Systemic routes:")
        for route in systemic_data['administration_route'].value_counts().items():
            print(f"    {route[0]}: {route[1]} data points")
        
        print(f"  Tissue-matched local routes:")
        for route in local_data['administration_route'].value_counts().items():
            print(f"    {route[0]}: {route[1]} data points")
        
        # Create comparison plot
        compare_routes_for_tissue_matched(tissue, systemic_data, local_data, 
                                         systemic_routes, local_routes, output_dir)

def compare_routes_for_tissue_matched(tissue, systemic_data, local_data, 
                                      systemic_routes, local_routes, output_dir):
    """
    Compare systemic vs tissue-matched local routes for a specific tissue
    """
    
    common_serotypes = (set(systemic_data['serotype'].unique()) & 
                       set(local_data['serotype'].unique()))
    
    if len(common_serotypes) < 2:
        return
    
    comparison_data = pd.DataFrame({
        'Systemic': systemic_data.groupby('serotype')['normalized_score'].mean(),
        'Local (Tissue-Matched)': local_data.groupby('serotype')['normalized_score'].mean()
    })
    
    comparison_data['Enhancement'] = (
        comparison_data['Local (Tissue-Matched)'] / comparison_data['Systemic']
    )
    
    # Create figure
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    # 1. Heatmap
    sns.heatmap(
        comparison_data[['Systemic', 'Local (Tissue-Matched)']],
        annot=True, fmt='.2f', cmap='YlOrRd', vmin=0, vmax=5,
        linewidths=0.5, ax=ax1
    )
    ax1.set_title(f'{tissue}\nSystemic vs Local', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Serotype', fontsize=10, fontweight='bold')
    
    # 2. Scatter
    ax2.scatter(comparison_data['Systemic'], 
               comparison_data['Local (Tissue-Matched)'],
               s=100, alpha=0.6, c='steelblue')
    ax2.plot([0, 5], [0, 5], 'r--', alpha=0.5, label='Equal')
    
    for idx, row in comparison_data.iterrows():
        ax2.annotate(idx, (row['Systemic'], row['Local (Tissue-Matched)']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax2.set_xlabel('Systemic Score', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Local Score', fontsize=10, fontweight='bold')
    ax2.set_title('Correlation', fontsize=12, fontweight='bold')
    ax2.set_xlim(0, 5)
    ax2.set_ylim(0, 5)
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # 3. Enhancement bars
    comparison_data['Enhancement'].plot(kind='barh', ax=ax3, color='coral')
    ax3.axvline(x=1, color='red', linestyle='--', alpha=0.5, label='No enhancement')
    ax3.set_xlabel('Fold Enhancement\n(Local / Systemic)', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Serotype', fontsize=10, fontweight='bold')
    ax3.set_title('Local Enhancement', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(axis='x', alpha=0.3)
    
    # Add route details
    route_text = f"Systemic: {', '.join(systemic_routes[:2])}\n"
    route_text += f"Local: {', '.join(local_routes[:2])}"
    fig.text(0.5, 0.02, route_text, ha='center', fontsize=9, 
            style='italic', color='gray')
    
    plt.suptitle(f'{tissue}: Tissue-Matched Route Comparison', 
                fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    tissue_safe = tissue.lower().replace(' ', '_')
    output_file = f"{output_dir}/route_comparison_matched_{tissue_safe}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    
    plt.close()


def compare_qpcr_vs_luciferase_improved(df, output_dir='results/figures'):
    """
    Improved comparison with tissue-matched route separation
    """
    
    print("\n" + "="*70)
    print("COMPARING qPCR vs LUCIFERASE (TISSUE-MATCHED ROUTES)")
    print("="*70)
    
    qpcr_data = df[df['measurement_method'].str.contains('qPCR|PCR', case=False, na=False)].copy()
    luc_data = df[df['measurement_method'].str.contains('Luciferase', case=False, na=False)].copy()
    
    tissue_routes = get_tissue_specific_local_routes()
    systemic_routes = get_systemic_routes()
    
    common_tissues = set(qpcr_data['tissue'].unique()) & set(luc_data['tissue'].unique())
    
    if not common_tissues:
        print("  ⚠ No tissues with both qPCR and Luciferase data")
        return
    
    for tissue in sorted(common_tissues):
        qpcr_tissue = qpcr_data[qpcr_data['tissue'] == tissue]
        luc_tissue = luc_data[luc_data['tissue'] == tissue]
        
        # Get tissue-specific local routes
        local_routes = tissue_routes.get(tissue, [])
        
        # Categorize routes for this tissue
        def categorize_route(route):
            if route in systemic_routes:
                return 'Systemic'
            elif local_routes and route in local_routes:
                return 'Local'
            else:
                return None  # Not relevant for this tissue
        
        qpcr_tissue['route_type'] = qpcr_tissue['administration_route'].apply(categorize_route)
        luc_tissue['route_type'] = luc_tissue['administration_route'].apply(categorize_route)
        
        # Filter out non-relevant routes
        qpcr_tissue = qpcr_tissue[qpcr_tissue['route_type'].notna()]
        luc_tissue = luc_tissue[luc_tissue['route_type'].notna()]
        
        # Check what route types we have for both methods
        qpcr_route_types = set(qpcr_tissue['route_type'].unique())
        luc_route_types = set(luc_tissue['route_type'].unique())
        common_route_types = qpcr_route_types & luc_route_types
        
        if not common_route_types:
            print(f"\n  ⚠ {tissue}: No common route types between qPCR and Luciferase")
            continue
        
        print(f"\n{tissue}:")
        print(f"  Route types available: {sorted(common_route_types)}")
        if local_routes:
            print(f"  Tissue-specific local routes: {local_routes[:3]}...")
        
        # Analyze each route type separately
        for route_type in sorted(common_route_types):
            qpcr_route = qpcr_tissue[qpcr_tissue['route_type'] == route_type]
            luc_route = luc_tissue[luc_tissue['route_type'] == route_type]
            
            common_serotypes = (set(qpcr_route['serotype'].unique()) & 
                               set(luc_route['serotype'].unique()))
            
            if len(common_serotypes) < 2:
                print(f"    ⚠ {route_type}: Too few common serotypes ({len(common_serotypes)})")
                continue
            
            print(f"  Analyzing {route_type}: {len(common_serotypes)} serotypes")
            
            comparison_data = pd.DataFrame({
                'qPCR (Delivery)': qpcr_route.groupby('serotype')['normalized_score'].mean(),
                'Luciferase (Function)': luc_route.groupby('serotype')['normalized_score'].mean()
            })
            
            # Calculate metrics
            comparison_data['Weighted_Score'] = (
                0.4 * comparison_data['qPCR (Delivery)'] + 
                0.6 * comparison_data['Luciferase (Function)']
            )
            
            comparison_data['Overall_Tropism'] = np.sqrt(
                comparison_data['qPCR (Delivery)'] * comparison_data['Luciferase (Function)']
            )
            
            # Create figure
            fig = plt.figure(figsize=(16, 10))
            gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # 1. Heatmap
            ax1 = fig.add_subplot(gs[0, 0])
            sns.heatmap(
                comparison_data[['qPCR (Delivery)', 'Luciferase (Function)']],
                annot=True, fmt='.2f', cmap='YlOrRd', vmin=0, vmax=5,
                linewidths=0.5, ax=ax1
            )
            ax1.set_title(f'Delivery vs Function\n{route_type}', 
                         fontsize=12, fontweight='bold')
            ax1.set_ylabel('Serotype', fontsize=10, fontweight='bold')
            
            # 2. Scatter plot
            ax2 = fig.add_subplot(gs[0, 1])
            ax2.scatter(comparison_data['qPCR (Delivery)'], 
                       comparison_data['Luciferase (Function)'],
                       s=120, alpha=0.6, c='steelblue', edgecolors='black', linewidth=1)
            ax2.plot([0, 5], [0, 5], 'r--', alpha=0.5, linewidth=2, label='1:1')
            
            for idx, row in comparison_data.iterrows():
                ax2.annotate(idx, (row['qPCR (Delivery)'], row['Luciferase (Function)']),
                            xytext=(5, 5), textcoords='offset points', 
                            fontsize=9, fontweight='bold')
            
            ax2.set_xlabel('qPCR (Delivery)', fontsize=10, fontweight='bold')
            ax2.set_ylabel('Luciferase (Function)', fontsize=10, fontweight='bold')
            ax2.set_title(f'Correlation - {route_type}', fontsize=12, fontweight='bold')
            ax2.set_xlim(0, 5.2)
            ax2.set_ylim(0, 5.2)
            ax2.legend(fontsize=9)
            ax2.grid(alpha=0.3)
            
            # 3. Weighted Score
            ax3 = fig.add_subplot(gs[1, 0])
            comparison_data_sorted = comparison_data.sort_values('Weighted_Score', ascending=True)
            comparison_data_sorted['Weighted_Score'].plot(kind='barh', ax=ax3, 
                                                          color='purple', alpha=0.7)
            ax3.set_xlabel('Weighted Tropism Score', fontsize=10, fontweight='bold')
            ax3.set_ylabel('Serotype', fontsize=10, fontweight='bold')
            ax3.set_title('Weighted Score (40% Delivery + 60% Function)\n' + 
                         'Recommended for Therapeutic Selection', 
                         fontsize=11, fontweight='bold')
            ax3.set_xlim(0, 5)
            ax3.axvline(x=2.5, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
            ax3.grid(axis='x', alpha=0.3)
            
            for i, (idx, val) in enumerate(comparison_data_sorted['Weighted_Score'].items()):
                ax3.text(val + 0.1, i, f'{val:.2f}', va='center', 
                        fontsize=9, fontweight='bold')
            
            # 4. Overall Tropism
            ax4 = fig.add_subplot(gs[1, 1])
            comparison_data_sorted = comparison_data.sort_values('Overall_Tropism', ascending=True)
            comparison_data_sorted['Overall_Tropism'].plot(kind='barh', ax=ax4, 
                                                           color='darkred', alpha=0.7)
            ax4.set_xlabel('Overall Tropism Score', fontsize=10, fontweight='bold')
            ax4.set_ylabel('Serotype', fontsize=10, fontweight='bold')
            ax4.set_title('Overall Tropism √(Delivery × Function)\n' +
                         'Penalizes Imbalanced Performance', 
                         fontsize=11, fontweight='bold')
            ax4.set_xlim(0, 5)
            ax4.axvline(x=2.5, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
            ax4.grid(axis='x', alpha=0.3)
            
            for i, (idx, val) in enumerate(comparison_data_sorted['Overall_Tropism'].items()):
                ax4.text(val + 0.1, i, f'{val:.2f}', va='center', 
                        fontsize=9, fontweight='bold')
            
            # Add route information
            route_info = f"Route: {route_type}"
            if route_type == 'Local' and local_routes:
                route_info += f"\nLocal routes: {', '.join(local_routes[:2])}"
            elif route_type == 'Systemic':
                route_info += f"\nSystemic routes: IV, Retro-orbital"
            
            fig.text(0.5, 0.02, route_info, ha='center', fontsize=9, 
                    style='italic', color='gray')
            
            plt.suptitle(f'{tissue} - {route_type}: qPCR vs Luciferase Analysis', 
                        fontsize=14, fontweight='bold', y=0.98)
            
            tissue_safe = tissue.lower().replace(' ', '_')
            route_safe = route_type.lower()
            output_file = f"{output_dir}/qpcr_vs_luc_{tissue_safe}_{route_safe}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"    ✓ Saved: qpcr_vs_luc_{tissue_safe}_{route_safe}.png")
            plt.close()
            
            # Save rankings
            rankings = pd.DataFrame({
                'Weighted_Rank': comparison_data['Weighted_Score'].rank(ascending=False),
                'Overall_Rank': comparison_data['Overall_Tropism'].rank(ascending=False)
            })
            rankings['Consensus_Rank'] = rankings.mean(axis=1).rank()
            
            rankings_output = comparison_data[['qPCR (Delivery)', 'Luciferase (Function)', 
                                              'Weighted_Score', 'Overall_Tropism']]
            rankings_output['Weighted_Rank'] = rankings['Weighted_Rank']
            rankings_output['Overall_Rank'] = rankings['Overall_Rank']
            rankings_output['Consensus_Rank'] = rankings['Consensus_Rank']
            rankings_output['Route_Type'] = route_type
            rankings_output = rankings_output.sort_values('Consensus_Rank')
            
            csv_file = f"{output_dir}/rankings_{tissue_safe}_{route_safe}.csv"
            rankings_output.to_csv(csv_file)
            print(f"    ✓ Saved: rankings_{tissue_safe}_{route_safe}.csv")
            
            # Print top 3
            print(f"    Top 3 serotypes for {tissue} ({route_type}):")
            for i, (idx, row) in enumerate(rankings_output.head(3).iterrows(), 1):
                print(f"      {i}. {idx}: Weighted={row['Weighted_Score']:.2f}, " +
                      f"Overall={row['Overall_Tropism']:.2f} " +
                      f"(qPCR={row['qPCR (Delivery)']:.2f}, " +
                      f"Luc={row['Luciferase (Function)']:.2f})")

def create_method_route_matrix(df, output_dir='results/figures'):
    """
    Create comprehensive matrix showing Method × Route × Tissue
    """
    
    print("\n" + "="*70)
    print("GENERATING METHOD × ROUTE MATRIX")
    print("="*70)
    
    # Categorize methods and routes
    def categorize_method(method):
        method_lower = str(method).lower()
        if 'qpcr' in method_lower or 'pcr' in method_lower:
            return 'qPCR'
        elif 'luciferase' in method_lower:
            return 'Luciferase'
        else:
            return 'Other'
    
    systemic_routes = ['IV', 'Intravenous', 'Tail vein', 'Retro-orbital', 'Facial vein']
    
    def categorize_route(route):
        return 'Systemic' if route in systemic_routes else 'Local'
    
    df['method_cat'] = df['measurement_method'].apply(categorize_method)
    df['route_cat'] = df['administration_route'].apply(categorize_route)
    
    # Create method-route combination
    df['method_route'] = df['method_cat'] + '\n' + df['route_cat']
    
    # Filter to qPCR and Luciferase only
    df_filtered = df[df['method_cat'].isin(['qPCR', 'Luciferase'])]
    
    if len(df_filtered) == 0:
        print("  ⚠ No qPCR or Luciferase data")
        return
    
    # Create pivot table
    matrix_data = df_filtered.pivot_table(
        values='normalized_score',
        index='tissue',
        columns='method_route',
        aggfunc='mean'
    )
    
    # Reorder columns for better visualization
    desired_order = ['qPCR\nSystemic', 'qPCR\nLocal', 
                    'Luciferase\nSystemic', 'Luciferase\nLocal']
    available_cols = [col for col in desired_order if col in matrix_data.columns]
    matrix_data = matrix_data[available_cols]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(
        matrix_data,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        vmin=0,
        vmax=5,
        cbar_kws={'label': 'Tropism Score (0-5)'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title('AAV Tropism: Method × Route × Tissue Matrix\n' +
                'Delivery (qPCR) vs Function (Luciferase) by Route',
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Measurement Method & Route', fontsize=11, fontweight='bold')
    ax.set_ylabel('Tissue', fontsize=11, fontweight='bold')
    
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='center')
    
    # Add dividing line between qPCR and Luciferase
    if len(available_cols) > 2:
        ax.axvline(x=2, color='blue', linewidth=2, alpha=0.7)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/method_route_tissue_matrix.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved method×route matrix: {output_file}")
    
    # Save data
    matrix_data.to_csv(f"{output_dir}/method_route_tissue_matrix.csv")
    print(f"✓ Saved matrix CSV")
    
    plt.close()
    
    # Print summary statistics
    print("\nSummary by Method and Route:")
    summary = df_filtered.groupby(['method_cat', 'route_cat'])['normalized_score'].agg(['mean', 'std', 'count'])
    print(summary)

def analyze_expression_efficiency_by_route(df, output_dir='results/figures'):
    """
    Analyze expression efficiency (Luciferase/qPCR ratio) by route
    """
    
    print("\n" + "="*70)
    print("ANALYZING EXPRESSION EFFICIENCY BY ROUTE")
    print("="*70)
    
    # Get qPCR and Luciferase data
    qpcr_data = df[df['measurement_method'].str.contains('qPCR|PCR', case=False, na=False)].copy()
    luc_data = df[df['measurement_method'].str.contains('Luciferase', case=False, na=False)].copy()
    
    # Categorize routes
    systemic_routes = ['IV', 'Intravenous', 'Tail vein', 'Retro-orbital', 'Facial vein']
    
    def categorize_route(route):
        return 'Systemic' if route in systemic_routes else 'Local'
    
    qpcr_data['route_type'] = qpcr_data['administration_route'].apply(categorize_route)
    luc_data['route_type'] = luc_data['administration_route'].apply(categorize_route)
    
    # Calculate efficiency for each tissue-serotype-route combination
    efficiency_data = []
    
    for tissue in df['tissue'].unique():
        for serotype in df['serotype'].unique():
            for route_type in ['Systemic', 'Local']:
                qpcr_vals = qpcr_data[
                    (qpcr_data['tissue'] == tissue) &
                    (qpcr_data['serotype'] == serotype) &
                    (qpcr_data['route_type'] == route_type)
                ]['normalized_score']
                
                luc_vals = luc_data[
                    (luc_data['tissue'] == tissue) &
                    (luc_data['serotype'] == serotype) &
                    (luc_data['route_type'] == route_type)
                ]['normalized_score']
                
                if len(qpcr_vals) > 0 and len(luc_vals) > 0:
                    qpcr_mean = qpcr_vals.mean()
                    luc_mean = luc_vals.mean()
                    
                    if qpcr_mean > 0:  # Avoid division by zero
                        efficiency = luc_mean / qpcr_mean
                        
                        efficiency_data.append({
                            'Tissue': tissue,
                            'Serotype': serotype,
                            'Route': route_type,
                            'qPCR_Score': qpcr_mean,
                            'Luciferase_Score': luc_mean,
                            'Expression_Efficiency': efficiency
                        })
    
    if not efficiency_data:
        print("  ⚠ No matching data for efficiency calculation")
        return
    
    efficiency_df = pd.DataFrame(efficiency_data)
    
    print(f"\nCalculated efficiency for {len(efficiency_df)} combinations")
    
    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Box plot by route
    efficiency_df.boxplot(column='Expression_Efficiency', by='Route', ax=ax1)
    ax1.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Delivery = Function')
    ax1.set_title('Expression Efficiency by Route', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Administration Route', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Expression Efficiency\n(Luciferase / qPCR)', fontsize=11, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    plt.sca(ax1)
    plt.xticks(rotation=0)
    
    # Scatter plot: Systemic vs Local efficiency
    systemic_eff = efficiency_df[efficiency_df['Route'] == 'Systemic'].set_index(['Tissue', 'Serotype'])
    local_eff = efficiency_df[efficiency_df['Route'] == 'Local'].set_index(['Tissue', 'Serotype'])
    
    # Find common combinations
    common_idx = systemic_eff.index.intersection(local_eff.index)
    
    if len(common_idx) > 0:
        x_vals = systemic_eff.loc[common_idx, 'Expression_Efficiency']
        y_vals = local_eff.loc[common_idx, 'Expression_Efficiency']
        
        ax2.scatter(x_vals, y_vals, s=100, alpha=0.6, c='steelblue')
        
        # Diagonal line
        max_val = max(x_vals.max(), y_vals.max())
        ax2.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='Equal efficiency')
        
        # Label points
        for idx, (x, y) in enumerate(zip(x_vals, y_vals)):
            tissue, serotype = common_idx[idx]
            ax2.annotate(f"{serotype}\n{tissue[:4]}", (x, y),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=7, alpha=0.7)
        
        ax2.set_xlabel('Systemic Efficiency', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Local Efficiency', fontsize=11, fontweight='bold')
        ax2.set_title('Expression Efficiency:\nSystemic vs Local', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        # Add interpretation
        above = (y_vals > x_vals).sum()
        below = (y_vals < x_vals).sum()
        
        interp = f"Above line: {above}\n(Local more efficient)\n\nBelow line: {below}\n(Systemic more efficient)"
        ax2.text(0.05, 0.95, interp, transform=ax2.transAxes,
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/expression_efficiency_by_route.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved efficiency analysis: {output_file}")
    
    # Save data
    efficiency_df.to_csv(f"{output_dir}/expression_efficiency_by_route.csv", index=False)
    print(f"✓ Saved efficiency data CSV")
    
    # Print summary
    print("\nExpression Efficiency Summary:")
    print(efficiency_df.groupby('Route')['Expression_Efficiency'].describe())
    
    plt.close()

def main():
    """
    Main execution: Generate all heatmaps and visualizations
    """
    
    print("="*70)
    print("AAV TROPISM HEATMAP GENERATOR")
    print("WITH qPCR vs LUCIFERASE AND ROUTE DISTINCTION")
    print("="*70)
    
    # Load data
    df = load_normalized_data()
    
    if df is None:
        return
    
    # Create output directory
    output_dir = 'results/figures'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate all visualizations
    try:
        # 1. Main heatmap (all data combined)
        heatmap_data, count_data = create_tropism_heatmap(df, output_dir)
        
        # 2. Method-specific heatmaps (qPCR vs Luciferase)
        create_method_specific_heatmaps(df, output_dir)
        
        # 3. Direct qPCR vs Luciferase comparison
        compare_qpcr_vs_luciferase(df, output_dir)
        
        # 4. NEW: qPCR vs Luciferase BY ROUTE
        compare_qpcr_vs_luciferase_improved(df, output_dir)
        
        # 5. NEW: Method × Route matrix
        create_method_route_matrix(df, output_dir)
        
        # 6. NEW: Expression efficiency by route
        analyze_expression_efficiency_by_route(df, output_dir)
        
        # 7. Method comparison summary
        create_method_comparison_summary(df, output_dir)
        
        # 8. Combined heatmap with method indicators
        create_combined_heatmap_with_method_indicator(df, output_dir)
        
        # 9. Heatmap with counts
        create_heatmap_with_counts(df, output_dir)
        
        # 10. Tissue-specific heatmaps
        create_tissue_specific_heatmaps(df, output_dir)
        
        # 11. Summary statistics
        create_summary_statistics(df, output_dir)
        
        # 12. Data coverage
        create_data_coverage_plot(df, output_dir)
        
        # 13. Route-specific heatmaps
        create_route_specific_heatmaps(df, output_dir)
        
        # 14. Route comparison summary
        create_route_comparison_summary(df, output_dir)
        
        # 15. Analyze routes by tissue
        analyze_routes_by_tissue(df, output_dir)

        create_route_comparison_summary(df, output_dir)
        analyze_routes_by_tissue(df, output_dir)
        
        print("\n" + "="*70)
        print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
        print("="*70)
        print(f"\nOutput location: {output_dir}/")
        print("\nGenerated files:")
        print("  METHOD × ROUTE ANALYSIS:")
        print("    • qpcr_vs_luc_*_systemic.png - Method comparison for systemic delivery")
        print("    • qpcr_vs_luc_*_local.png - Method comparison for local delivery")
        print("    • method_route_tissue_matrix.png - Comprehensive Method×Route×Tissue matrix")
        print("    • expression_efficiency_by_route.png - Efficiency analysis by route")
        print("\n  METHOD-SPECIFIC:")
        print("    • tropism_heatmap_method_qpcr_delivery.png - Vector delivery")
        print("    • tropism_heatmap_method_luciferase_function.png - Functional transduction")
        print("    • qpcr_vs_luciferase_*.png - Direct comparisons by tissue")
        print("    • method_comparison_summary.png - Overall method comparison")
        print("    • tropism_heatmap_combined_with_method.png - Combined with indicators")
        print("\n  [... rest of files ...]")
        print("\n" + "="*70)
        print("METRIC INTERPRETATION GUIDE")
        print("="*70)
        print("""
        Expression Efficiency (Luc/qPCR):
        ⚠ Can be misleading! High ratio doesn't mean good performance.
        Use only when comparing serotypes with similar delivery.

        Average Performance:
        ✓ Simple and intuitive
        ✓ Rewards both delivery and function equally

        Minimum Score (Bottleneck):
        ✓ Conservative - limited by weaker metric
        ✓ Good for identifying balanced serotypes

        Weighted Score (40% Del + 60% Func):
        ✓ Prioritizes functional expression
        ✓ Best for therapeutic selection

        Overall Tropism (Geometric Mean):
        ✓ Penalizes imbalanced performance
        ✓ Rewards serotypes good at both

        RECOMMENDATION: Use Weighted Score or Overall Tropism for ranking.
        """)
        
    except Exception as e:
        print(f"\n✗ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
