"""
Create comprehensive Excel template with multiple examples
"""
import pandas as pd
import numpy as np

# Define columns
columns = [
    'paper_id', 'pmid', 'first_author', 'year', 'journal',
    'serotype', 'tissue', 'species', 'administration_route',
    'dose_vg_kg', 'timepoint_days', 'measurement_method',
    'raw_value', 'units', 'normalized_score', 'quality_score',
    'notes', 'figure_reference', 'extraction_date'
]

# Create comprehensive example data showing different scenarios
template_data = [
    # Example 1: Zincarelli 2008 - High quality qPCR data
    {
        'paper_id': 1,
        'pmid': '18432245',
        'first_author': 'Zincarelli',
        'year': 2008,
        'journal': 'Molecular Therapy',
        'serotype': 'AAV1',
        'tissue': 'Liver',
        'species': 'Mouse',
        'administration_route': 'IV',
        'dose_vg_kg': '1e11',
        'timepoint_days': 14,
        'measurement_method': 'qPCR',
        'raw_value': '5.2e9',
        'units': 'vg/ug DNA',
        'normalized_score': 4.5,
        'quality_score': 'High',
        'notes': 'C57BL/6 mice, n=3-5 per group, tail vein injection',
        'figure_reference': 'Figure 2A',
        'extraction_date': '2024-02-17'
    },
    {
        'paper_id': 1,
        'pmid': '18432245',
        'first_author': 'Zincarelli',
        'year': 2008,
        'journal': 'Molecular Therapy',
        'serotype': 'AAV1',
        'tissue': 'Brain',
        'species': 'Mouse',
        'administration_route': 'IV',
        'dose_vg_kg': '1e11',
        'timepoint_days': 14,
        'measurement_method': 'qPCR',
        'raw_value': '1.2e8',
        'units': 'vg/ug DNA',
        'normalized_score': 1.8,
        'quality_score': 'High',
        'notes': 'C57BL/6 mice, n=3-5 per group',
        'figure_reference': 'Figure 2A',
        'extraction_date': '2024-02-17'
    },
    {
        'paper_id': 1,
        'pmid': '18432245',
        'first_author': 'Zincarelli',
        'year': 2008,
        'journal': 'Molecular Therapy',
        'serotype': 'AAV2',
        'tissue': 'Liver',
        'species': 'Mouse',
        'administration_route': 'IV',
        'dose_vg_kg': '1e11',
        'timepoint_days': 14,
        'measurement_method': 'qPCR',
        'raw_value': '3.8e9',
        'units': 'vg/ug DNA',
        'normalized_score': 3.9,
        'quality_score': 'High',
        'notes': 'C57BL/6 mice, n=3-5 per group',
        'figure_reference': 'Figure 2A',
        'extraction_date': '2024-02-17'
    },
    
    # Example 2: Luciferase data
    {
        'paper_id': 2,
        'pmid': '26814963',
        'first_author': 'Deverman',
        'year': 2016,
        'journal': 'Nature Biotechnology',
        'serotype': 'AAV-PHP.eB',
        'tissue': 'Brain',
        'species': 'Mouse',
        'administration_route': 'IV',
        'dose_vg_kg': '1e11',
        'timepoint_days': 21,
        'measurement_method': 'Luciferase',
        'raw_value': '1.5e6',
        'units': 'RLU',
        'normalized_score': 4.2,
        'quality_score': 'High',
        'notes': 'C57BL/6J mice, n=3, retro-orbital injection',
        'figure_reference': 'Figure 1c',
        'extraction_date': '2024-02-17'
    },
    
    # Example 3: Percentage data (GFP/IHC)
    {
        'paper_id': 2,
        'pmid': '26814963',
        'first_author': 'Deverman',
        'year': 2016,
        'journal': 'Nature Biotechnology',
        'serotype': 'AAV9',
        'tissue': 'Brain',
        'species': 'Mouse',
        'administration_route': 'IV',
        'dose_vg_kg': '1e11',
        'timepoint_days': 21,
        'measurement_method': 'GFP',
        'raw_value': '15',
        'units': '% positive cells',
        'normalized_score': 0.75,
        'quality_score': 'High',
        'notes': 'C57BL/6J mice, n=3, cortical neurons',
        'figure_reference': 'Figure 1c',
        'extraction_date': '2024-02-17'
    },
    
    # Example 4: NHP data
    {
        'paper_id': 3,
        'pmid': '25847991',
        'first_author': 'Wang',
        'year': 2015,
        'journal': 'Molecular Therapy',
        'serotype': 'AAVrh10',
        'tissue': 'Liver',
        'species': 'NHP',
        'administration_route': 'IV',
        'dose_vg_kg': '2e13',
        'timepoint_days': 28,
        'measurement_method': 'qPCR',
        'raw_value': '8.5e9',
        'units': 'vg/ug DNA',
        'normalized_score': 4.8,
        'quality_score': 'High',
        'notes': 'Rhesus macaques, n=3, peripheral vein',
        'figure_reference': 'Figure 3B',
        'extraction_date': '2024-02-17'
    },
    
    # Example 5: Medium quality data
    {
        'paper_id': 4,
        'pmid': 'XXXXXXXX',
        'first_author': 'Example',
        'year': 2020,
        'journal': 'Gene Therapy',
        'serotype': 'AAV8',
        'tissue': 'Muscle',
        'species': 'Mouse',
        'administration_route': 'IM',
        'dose_vg_kg': '5e10',
        'timepoint_days': 7,
        'measurement_method': 'IHC',
        'raw_value': '3',
        'units': 'semi-quantitative (0-4)',
        'normalized_score': 3.75,
        'quality_score': 'Medium',
        'notes': 'BALB/c mice, n=3, no negative control reported',
        'figure_reference': 'Figure 4A',
        'extraction_date': '2024-02-17'
    }
]

# Create DataFrame
df_template = pd.DataFrame(template_data)

# Save as Excel with multiple sheets
with pd.ExcelWriter('data/metadata/tropism_extraction_template.xlsx', engine='openpyxl') as writer:
    # Sheet 1: Data entry template
    df_template.to_excel(writer, sheet_name='Data', index=False)
    
    # Sheet 2: Instructions
    instructions = pd.DataFrame({
        'Column': columns,
        'Description': [
            'Unique paper identifier (sequential: 1, 2, 3...)',
            'PubMed ID (e.g., 18432245)',
            'First author last name',
            'Publication year',
            'Journal name',
            'AAV serotype (AAV1, AAV2, AAV-PHP.eB, MyoAAV1A, etc.)',
            'Target tissue/organ (Liver, Brain, Heart, Skeletal Muscle, etc.)',
            'Species (Mouse, Rat, NHP, Human)',
            'Route (IV, IM, ICV, IT, IP, etc.)',
            'Dose in vg/kg (use scientific notation: 1e11, 5e12)',
            'Days after injection (7, 14, 21, 28, etc.)',
            'Method (qPCR, Luciferase, GFP, IHC, Western, etc.)',
            'Raw value from paper (use scientific notation if needed)',
            'Units (vg/ug DNA, RLU, %, fold-change, etc.)',
            'Normalized to 0-5 scale (calculate or leave blank)',
            'High, Medium, or Low',
            'Sample size, strain, controls, any caveats',
            'Figure/Table reference (Figure 2A, Table 1, Supp Fig 3)',
            'Date you extracted this data (YYYY-MM-DD)'
        ],
        'Example': [
            '1',
            '18432245',
            'Zincarelli',
            '2008',
            'Molecular Therapy',
            'AAV1',
            'Liver',
            'Mouse',
            'IV',
            '1e11',
            '14',
            'qPCR',
            '5.2e9',
            'vg/ug DNA',
            '4.5',
            'High',
            'C57BL/6 mice, n=5',
            'Figure 2A',
            '2024-02-17'
        ]
    })
    instructions.to_excel(writer, sheet_name='Instructions', index=False)
    
    # Sheet 3: Normalization formulas
    normalization = pd.DataFrame({
        'Method': ['qPCR', 'Luciferase', 'GFP/IHC (%)', 'Semi-quantitative', 'Fold-change'],
        'Typical_Range': ['1e6 - 1e10 vg/ug DNA', '1e3 - 1e8 RLU', '0-100%', '0-4 scale', '1-1000x'],
        'Formula': [
            'log_value = log10(raw_value); normalized = (log_value - 6) / 4 * 5',
            'log_value = log10(raw_value); normalized = (log_value - 3) / 5 * 5',
            'normalized = (raw_value / 100) * 5',
            'normalized = raw_value * 1.25',
            'log_value = log10(raw_value); normalized = (log_value / 3) * 5'
        ],
        'Example_Input': ['5.2e9', '1.5e6', '85', '3', '100'],
        'Example_Output': ['4.5', '4.2', '4.25', '3.75', '3.3']
    })
    normalization.to_excel(writer, sheet_name='Normalization', index=False)
    
    # Sheet 4: Quality criteria
    quality = pd.DataFrame({
        'Quality': ['High', 'High', 'High', 'High', 'Medium', 'Medium', 'Medium', 'Low', 'Low', 'Low'],
        'Criterion': [
            'Quantitative method (qPCR, Luciferase)',
            'Sample size n >= 5',
            'Appropriate controls included',
            'Statistical analysis reported',
            'Semi-quantitative method',
            'Sample size n = 3-4',
            'Some controls',
            'Qualitative only',
            'Sample size n < 3',
            'No controls reported'
        ],
        'Action': [
            'Use with confidence',
            'Use with confidence',
            'Use with confidence',
            'Use with confidence',
            'Use but note limitation',
            'Use but note limitation',
            'Use but note limitation',
            'Use cautiously, flag in notes',
            'Use cautiously, flag in notes',
            'Consider excluding'
        ]
    })
    quality.to_excel(writer, sheet_name='Quality_Criteria', index=False)
    
    # Sheet 5: Common tissues
    tissues = pd.DataFrame({
        'Tissue': [
            'Liver', 'Brain', 'Heart', 'Skeletal Muscle', 'Lung', 'Kidney',
            'Spleen', 'Pancreas', 'Retina', 'Spinal Cord', 'Cortex', 'Striatum',
            'Hippocampus', 'Cerebellum', 'Myocardium', 'Diaphragm', 'Gastrocnemius',
            'Quadriceps', 'Tibialis Anterior'
        ],
        'Category': [
            'Visceral', 'CNS', 'Cardiac', 'Muscle', 'Visceral', 'Visceral',
            'Lymphoid', 'Visceral', 'Sensory', 'CNS', 'CNS', 'CNS',
            'CNS', 'CNS', 'Cardiac', 'Muscle', 'Muscle',
            'Muscle', 'Muscle'
        ],
        'Notes': [
            'Primary target for many serotypes',
            'Whole brain (specify region if possible)',
            'Whole heart or specify chamber',
            'Specify muscle type if possible',
            'Respiratory tissue',
            'Renal tissue',
            'Immune organ',
            'Endocrine organ',
            'Eye tissue',
            'CNS tissue',
            'Brain region',
            'Brain region',
            'Brain region',
            'Brain region',
            'Heart muscle',
            'Respiratory muscle',
            'Leg muscle',
            'Leg muscle',
            'Leg muscle'
        ]
    })
    tissues.to_excel(writer, sheet_name='Common_Tissues', index=False)
    
    # Sheet 6: Progress tracker
    progress = pd.DataFrame({
        'Paper_ID': [1, 2, 3],
        'PMID': ['18432245', '26814963', '25847991'],
        'First_Author': ['Zincarelli', 'Deverman', 'Wang'],
        'Year': [2008, 2016, 2015],
        'Status': ['Complete', 'In Progress', 'Not Started'],
        'Data_Points_Extracted': [81, 15, 0],
        'Time_Spent_Minutes': [60, 20, 0],
        'Notes': ['All serotypes done', 'Need supplementary data', '']
    })
    progress.to_excel(writer, sheet_name='Progress_Tracker', index=False)

print("✓ Created comprehensive template: data/metadata/tropism_extraction_template.xlsx")
print("\nTemplate includes:")
print("  • Data sheet with examples")
print("  • Instructions for each column")
print("  • Normalization formulas")
print("  • Quality criteria")
print("  • Common tissue names")
print("  • Progress tracker")