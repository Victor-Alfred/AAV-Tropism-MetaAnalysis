"""
Create enhanced extraction template with cell type information
"""
import pandas as pd

# Enhanced columns with cell_type
columns = [
    'paper_id', 'pmid', 'first_author', 'year', 'journal',
    'serotype', 'promoter', 'transgene', 'capsid_modification',
    'tissue', 'cell_type', 'tissue_subtype',  # NEW: Cell-type specificity
    'species', 'strain', 'animal_age', 'animal_age_units', 'sex',
    'administration_route', 'injection_site',  
    'dose_vg_kg', 'dose_vg_total', 'timepoint_days', 'timepoint_weeks',
    'measurement_method', 'measurement_type',
    'raw_value', 'units', 'normalized_score',
    'sample_size', 'quality_score', 'notes', 'figure_reference', 'extraction_date',
    'immune_status', 'previous_exposure'
]

# Enhanced example data with cell type examples
template_data = [
    {
        'paper_id': 1,
        'pmid': '18432245',
        'first_author': 'Zincarelli',
        'year': 2008,
        'journal': 'Molecular Therapy',
        'serotype': 'AAV1',
        'promoter': 'CMV',
        'transgene': 'Luciferase',
        'capsid_modification': 'None',
        'tissue': 'Liver',
        'cell_type': None,  # Whole tissue measurement
        'tissue_subtype': None,
        'species': 'Mouse',
        'strain': 'C57BL/6',
        'animal_age': '8',
        'animal_age_units': 'weeks',
        'sex': 'Mixed',
        'administration_route': 'IV',
        'injection_site': 'Tail vein',
        'dose_vg_kg': '1e11',
        'dose_vg_total': '2e10',
        'timepoint_days': 14,
        'timepoint_weeks': 2,
        'measurement_method': 'qPCR',
        'measurement_type': 'Genome',
        'raw_value': '5.2e9',
        'units': 'vg/ug DNA',
        'normalized_score': 4.5,
        'sample_size': 5,
        'quality_score': 'High',
        'notes': 'C57BL/6 mice, immunocompetent, naive to AAV, whole liver homogenate',
        'figure_reference': 'Figure 2A',
        'extraction_date': '2024-02-17',
        'immune_status': 'Immunocompetent',
        'previous_exposure': 'Naive'
    },
    {
        'paper_id': 2,
        'pmid': '26814963',
        'first_author': 'Deverman',
        'year': 2016,
        'journal': 'Nature Biotechnology',
        'serotype': 'AAV-PHP.eB',
        'promoter': 'CAG',
        'transgene': 'GFP',
        'capsid_modification': 'PHP.eB (7-mer insertion)',
        'tissue': 'Brain',
        'cell_type': 'Neurons',  # Cell-type specific
        'tissue_subtype': 'Cortex',
        'species': 'Mouse',
        'strain': 'C57BL/6J',
        'animal_age': '8-10',
        'animal_age_units': 'weeks',
        'sex': 'Mixed',
        'administration_route': 'IV',
        'injection_site': 'Retro-orbital',
        'dose_vg_kg': '1e11',
        'dose_vg_total': '2e10',
        'timepoint_days': 21,
        'timepoint_weeks': 3,
        'measurement_method': 'GFP/mCherry',
        'measurement_type': 'Expression',
        'raw_value': '85',
        'units': '% positive cells',
        'normalized_score': 4.25,
        'sample_size': 3,
        'quality_score': 'High',
        'notes': 'Cortical neurons, immunocompetent, neuron-specific quantification',
        'figure_reference': 'Figure 1c',
        'extraction_date': '2024-02-17',
        'immune_status': 'Immunocompetent',
        'previous_exposure': 'Naive'
    },
    {
        'paper_id': 3,
        'pmid': '19144878',
        'first_author': 'Foust',
        'year': 2009,
        'journal': 'Nature Biotechnology',
        'serotype': 'AAV9',
        'promoter': 'CB',
        'transgene': 'GFP',
        'capsid_modification': 'None',
        'tissue': 'Brain',
        'cell_type': None,  # Mixed cell types
        'tissue_subtype': None,
        'species': 'Mouse',
        'strain': 'C57BL/6',
        'animal_age': '1',
        'animal_age_units': 'days',
        'sex': 'Mixed',
        'administration_route': 'IV',
        'injection_site': 'Facial vein',
        'dose_vg_kg': '5e11',
        'dose_vg_total': '5e9',
        'timepoint_days': 21,
        'timepoint_weeks': 3,
        'measurement_method': 'qPCR',
        'measurement_type': 'Genome',
        'raw_value': '8.5e8',
        'units': 'vg/ug DNA',
        'normalized_score': 3.56,
        'sample_size': 4,
        'quality_score': 'High',
        'notes': 'NEONATAL mice - critical for interpretation! Whole brain homogenate',
        'figure_reference': 'Figure 3',
        'extraction_date': '2024-02-17',
        'immune_status': 'Immunocompetent',
        'previous_exposure': 'Naive'
    },
    {
        'paper_id': 4,
        'pmid': 'Example1',
        'first_author': 'Example',
        'year': 2020,
        'journal': 'Example Journal',
        'serotype': 'AAV-Anc80',
        'promoter': 'CAG',
        'transgene': 'GFP',
        'capsid_modification': 'Ancestral reconstruction',
        'tissue': 'Cochlea',
        'cell_type': 'Inner Hair Cells',  # Specific cochlear cell type
        'tissue_subtype': 'Apex',
        'species': 'Mouse',
        'strain': 'CBA/J',
        'animal_age': '6',
        'animal_age_units': 'weeks',
        'sex': 'Mixed',
        'administration_route': 'Round window injection',
        'injection_site': 'Round window membrane',
        'dose_vg_kg': None,
        'dose_vg_total': '1e9',
        'timepoint_days': 14,
        'timepoint_weeks': 2,
        'measurement_method': 'GFP/mCherry',
        'measurement_type': 'Expression',
        'raw_value': '85',
        'units': '%',
        'normalized_score': 4.25,
        'sample_size': 5,
        'quality_score': 'High',
        'notes': 'Inner hair cells in apical turn, excellent transduction',
        'figure_reference': 'Figure 4A',
        'extraction_date': '2024-02-17',
        'immune_status': 'Immunocompetent',
        'previous_exposure': 'Naive'
    },
    {
        'paper_id': 5,
        'pmid': 'Example2',
        'first_author': 'Example',
        'year': 2020,
        'journal': 'Example Journal',
        'serotype': 'AAV-Anc80',
        'promoter': 'CAG',
        'transgene': 'GFP',
        'capsid_modification': 'Ancestral reconstruction',
        'tissue': 'Cochlea',
        'cell_type': 'Outer Hair Cells',  # Different cochlear cell type
        'tissue_subtype': 'Apex',
        'species': 'Mouse',
        'strain': 'CBA/J',
        'animal_age': '6',
        'animal_age_units': 'weeks',
        'sex': 'Mixed',
        'administration_route': 'Round window injection',
        'injection_site': 'Round window membrane',
        'dose_vg_kg': None,
        'dose_vg_total': '1e9',
        'timepoint_days': 14,
        'timepoint_weeks': 2,
        'measurement_method': 'GFP/mCherry',
        'measurement_type': 'Expression',
        'raw_value': '65',
        'units': '%',
        'normalized_score': 3.25,
        'sample_size': 5,
        'quality_score': 'High',
        'notes': 'Outer hair cells (3 rows) in apical turn, lower than IHCs',
        'figure_reference': 'Figure 4B',
        'extraction_date': '2024-02-17',
        'immune_status': 'Immunocompetent',
        'previous_exposure': 'Naive'
    },
    {
        'paper_id': 6,
        'pmid': 'Example3',
        'first_author': 'Example',
        'year': 2021,
        'journal': 'Example Journal',
        'serotype': 'AAV9',
        'promoter': 'Synapsin',
        'transgene': 'GFP',
        'capsid_modification': 'None',
        'tissue': 'Enteric Nervous System',
        'cell_type': 'Neurons',
        'tissue_subtype': 'Myenteric Plexus',
        'species': 'Mouse',
        'strain': 'C57BL/6',
        'animal_age': '8',
        'animal_age_units': 'weeks',
        'sex': 'Male',
        'administration_route': 'IV',
        'injection_site': 'Tail vein',
        'dose_vg_kg': '1e11',
        'dose_vg_total': '2e10',
        'timepoint_days': 28,
        'timepoint_weeks': 4,
        'measurement_method': 'GFP/mCherry',
        'measurement_type': 'Expression',
        'raw_value': '450',
        'units': 'cells/mm2',
        'normalized_score': 4.13,
        'sample_size': 5,
        'quality_score': 'High',
        'notes': 'Myenteric plexus neurons in colon, GFP+ cell density',
        'figure_reference': 'Figure 5',
        'extraction_date': '2024-02-17',
        'immune_status': 'Immunocompetent',
        'previous_exposure': 'Naive'
    }
]

# Create DataFrame
df_template = pd.DataFrame(template_data)

# Save as Excel with multiple sheets
with pd.ExcelWriter('data/metadata/tropism_extraction_template_enhanced.xlsx',  
                    engine='openpyxl') as writer:
    
    # Sheet 1: Data entry
    df_template.to_excel(writer, sheet_name='Data', index=False)
    
    # Sheet 2: Column descriptions
    descriptions = pd.DataFrame({
        'Column': columns,
        'Description': [
            'Unique paper identifier',
            'PubMed ID',
            'First author last name',
            'Publication year',
            'Journal name',
            'AAV serotype (AAV1-9, PHP variants, engineered)',
            'Promoter used (CMV, CAG, Synapsin, etc.)',
            'Transgene (GFP, Luciferase, etc.)',
            'Capsid modifications (if any)',
            'Primary tissue/organ category',
            'Specific cell type (Neurons, IHCs, OHCs, etc.)',
            'Tissue subtype or region (Cortex, Apex, Myenteric Plexus, etc.)',
            'Species (Mouse, Rat, NHP, Human)',
            'Mouse strain (C57BL/6, BALB/c, CBA/J, etc.)',
            'Animal age (number)',
            'Age units (days, weeks, months)',
            'Sex (M, F, Mixed)',
            'Administration route (IV, Intranasal, Round window, etc.)',
            'Specific injection site',
            'Dose per kg body weight (vg/kg)',
            'Total dose (if reported)',
            'Days post-injection',
            'Weeks post-injection',
            'Measurement method (qPCR, Luciferase, GFP, etc.)',
            'Type (Genome, Expression, Functional)',
            'Raw value from paper',
            'Units (vg/ug DNA, %, cells/mm2, RLU, etc.)',
            'Normalized to 0-5 scale',
            'Sample size (n)',
            'Data quality (High, Medium, Low)',
            'Additional notes and context',
            'Figure/Table reference',
            'Date extracted (YYYY-MM-DD)',
            'Immune status (Immunocompetent, Immunodeficient)',
            'Previous AAV exposure (Naive, Pre-exposed)'
        ],
        'Example': [
            '1',
            '18432245',
            'Zincarelli',
            '2008',
            'Molecular Therapy',
            'AAV1, AAV9, AAV-PHP.eB',
            'CMV, CAG, Synapsin',
            'Luciferase, GFP',
            'None, PHP.eB insertion',
            'Liver, Brain, Cochlea, Enteric Nervous System',
            'Neurons, Inner Hair Cells, Outer Hair Cells',
            'Cortex, Apex, Myenteric Plexus',
            'Mouse, Rat, NHP',
            'C57BL/6, CBA/J',
            '8, 1, 6',
            'weeks, days',
            'Mixed, M, F',
            'IV, Intranasal, Round window',
            'Tail vein, Round window membrane',
            '1e11',
            '2e10, 1e9',
            '14, 21, 28',
            '2, 3, 4',
            'qPCR, GFP/mCherry, Luciferase',
            'Genome, Expression',
            '5.2e9, 85, 450',
            'vg/ug DNA, %, cells/mm2',
            '4.5, 4.25, 4.13',
            '5, 3',
            'High, Medium, Low',
            'Context and important details',
            'Figure 2A, Figure 4B',
            '2024-02-17',
            'Immunocompetent',
            'Naive'
        ]
    })
    descriptions.to_excel(writer, sheet_name='Column_Descriptions', index=False)
    
    # Sheet 3: Cell type reference
    cell_types = pd.DataFrame({
        'Tissue': [
            'Brain', 'Brain', 'Brain', 'Brain',
            'Cochlea', 'Cochlea', 'Cochlea', 'Cochlea',
            'Retina', 'Retina', 'Retina',
            'Enteric Nervous System', 'Enteric Nervous System',
            'Olfactory Epithelium',
            'Skeletal Muscle',
            'Heart',
            'Liver'
        ],
        'Cell_Type': [
            'Neurons', 'Astrocytes', 'Oligodendrocytes', 'Microglia',
            'Inner Hair Cells', 'Outer Hair Cells', 'Spiral Ganglion Neurons', 'Supporting Cells',
            'Photoreceptors (Rods)', 'Photoreceptors (Cones)', 'Retinal Ganglion Cells',
            'Neurons', 'Neurons',
            'Olfactory Sensory Neurons',
            'Myocytes',
            'Cardiomyocytes',
            'Hepatocytes'
        ],
        'Tissue_Subtype_Examples': [
            'Cortex, Striatum, Hippocampus', None, None, None,
            'Apex, Base, Middle turn', 'Apex, Base, Middle turn', None, None,
            None, None, None,
            'Myenteric Plexus', 'Submucosal Plexus',
            None,
            None,
            'Left Ventricle, Right Ventricle',
            None
        ],
        'Notes': [
            'Specify brain region if reported',
            'Glial cells',
            'Myelin-forming cells',
            'Immune cells',
            'Sensory transduction, ~3,500 per cochlea',
            'Amplification, ~12,000 per cochlea, 3 rows',
            'Auditory nerve neurons',
            'Pillar cells, Deiters cells, etc.',
            'Low-light vision',
            'Color vision',
            'Transmit visual signal to brain',
            'Between muscle layers, controls motility',
            'In submucosa, controls secretion',
            'Nasal cavity, direct environmental exposure',
            'Skeletal muscle fibers',
            'Cardiac muscle cells',
            'Liver parenchymal cells'
        ]
    })
    cell_types.to_excel(writer, sheet_name='Cell_Type_Reference', index=False)
    
    # Sheet 4: Tissue categories
    tissues = pd.DataFrame({
        'Category': [
            'CNS', 'CNS', 'CNS',
            'Sensory', 'Sensory', 'Sensory',
            'PNS', 'PNS', 'PNS',
            'Muscle', 'Muscle', 'Muscle',
            'Visceral', 'Visceral', 'Visceral', 'Visceral', 'Visceral',
            'Reproductive'
        ],
        'Tissue': [
            'Brain', 'Spinal Cord', 'Olfactory Bulb',
            'Retina', 'Cochlea', 'Olfactory Epithelium',
            'Dorsal Root Ganglion', 'Peripheral Nerve', 'Enteric Nervous System',
            'Heart', 'Skeletal Muscle', 'Diaphragm',
            'Liver', 'Lung', 'Kidney', 'Spleen', 'Pancreas',
            'Testis/Ovary'
        ],
        'Use_Cell_Type': [
            'Yes', 'Yes', 'Yes',
            'Yes', 'Yes', 'Yes',
            'Optional', 'Optional', 'Yes',
            'Optional', 'No', 'No',
            'Optional', 'Optional', 'Optional', 'No', 'Optional',
            'Optional'
        ],
        'Notes': [
            'Specify neurons, astrocytes, etc. if reported',
            'Specify motor neurons, interneurons if reported',
            'Brain structure, part of CNS',
            'Specify photoreceptors, RGCs, etc.',
            'Specify IHCs, OHCs, SGNs, etc. - IMPORTANT',
            'Olfactory sensory neurons',
            'Sensory neurons',
            'Axons',
            'Specify myenteric vs submucosal plexus',
            'Specify cardiomyocytes if reported',
            'Whole muscle, no cell-type detail needed',
            'Respiratory muscle',
            'Specify hepatocytes if reported',
            'Specify cell type if reported',
            'Specify cell type if reported',
            'Whole organ',
            'Specify cell type if reported',
            'Whole organ'
        ]
    })
    tissues.to_excel(writer, sheet_name='Tissue_Categories', index=False)
    
    # Sheet 5: Promoter reference
    promoters = pd.DataFrame({
        'Promoter': [
            'CMV', 'CAG', 'CB', 'EF1α', 'PGK', 'UBC',
            'Synapsin', 'CaMKII', 'GFAP', 'MBP',
            'TTR', 'MCK', 'cTnT', 'Rhodopsin'
        ],
        'Type': [
            'Constitutive', 'Constitutive', 'Constitutive', 'Constitutive', 'Constitutive', 'Constitutive',
            'Neuron-specific', 'Excitatory neuron', 'Astrocyte', 'Oligodendrocyte',
            'Liver', 'Muscle', 'Cardiac', 'Photoreceptor'
        ],
        'Strength': [
            'Strong', 'Very Strong', 'Strong', 'Strong', 'Moderate', 'Strong',
            'Moderate', 'Strong', 'Moderate', 'Moderate',
            'Strong', 'Strong', 'Strong', 'Strong'
        ],
        'Notes': [
            'Most common, can silence over time',
            'Hybrid, very strong and stable',
            'Chicken β-actin, strong',
            'Elongation factor, stable',
            'Moderate, stable',
            'Ubiquitin, strong',
            'Neuron-specific, moderate strength',
            'Excitatory neurons only',
            'Astrocyte-specific',
            'Oligodendrocyte-specific',
            'Liver-specific',
            'Skeletal muscle-specific',
            'Cardiac muscle-specific',
            'Photoreceptor-specific'
        ]
    })
    promoters.to_excel(writer, sheet_name='Promoter_Reference', index=False)
    
    # Sheet 6: Age categories
    age_guide = pd.DataFrame({
        'Category': ['Neonatal', 'Juvenile', 'Young Adult', 'Adult', 'Aged'],
        'Age_Range': ['P0-P7', 'P7-P21', '6-12 weeks', '8+ weeks', '6+ months'],
        'BBB_Status': ['Immature', 'Developing', 'Mature', 'Mature', 'Mature'],
        'AAV9_CNS_Tropism': ['Very High', 'High', 'Moderate', 'Low-Moderate', 'Low'],
        'Notes': [
            'BBB immature, widespread CNS transduction',
            'BBB developing, good CNS access',
            'BBB mature, reduced CNS access',
            'Standard age for most studies',
            'Potential age-related changes'
        ]
    })
    age_guide.to_excel(writer, sheet_name='Age_Guide', index=False)
    
    # Sheet 7: Timepoint guide
    timepoint_guide = pd.DataFrame({
        'Category': ['Acute', 'Subacute', 'Chronic', 'Long-term'],
        'Days': ['1-7', '14-28', '56-90', '90+'],
        'Weeks': ['<1', '2-4', '8-12', '12+'],
        'Vector_Genomes': ['Peak', 'Stable', 'Declining', 'Low'],
        'Expression': ['Ramping up', 'Peak', 'Stable/Declining', 'Variable'],
        'Immune_Response': ['Minimal', 'Developing', 'Established', 'Chronic'],
        'Notes': [
            'Peak transduction, variable expression',
            'Most common timepoint, stable expression',
            'Potential clearance, immune effects',
            'Silencing possible, especially CMV'
        ]
    })
    timepoint_guide.to_excel(writer, sheet_name='Timepoint_Guide', index=False)

print("✓ Created enhanced template with cell type: data/metadata/tropism_extraction_template_enhanced.xlsx")
print("\nKey features:")
print("  • cell_type - Specific cell types (Neurons, IHCs, OHCs, etc.)")
print("  • tissue_subtype - Anatomical regions (Cortex, Apex, Myenteric Plexus)")
print("  • Complete reference sheets for cell types, tissues, promoters")
print("  • Examples showing proper usage")
print("\nNew reference sheets:")
print("  • Cell_Type_Reference - Common cell types by tissue")
print("  • Tissue_Categories - Organized tissue list with cell-type guidance")