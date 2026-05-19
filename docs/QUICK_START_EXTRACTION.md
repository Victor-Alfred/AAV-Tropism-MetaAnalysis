# Quick Start: Data Extraction

## Today's Goal (2-3 hours)

Extract data from **Zincarelli 2008** - the most important paper.

**Expected yield:** ~81 data points (9 serotypes × 9 tissues)

---


Week 1-2: DATA COLLECTION & NORMALIZATION
├── Extract raw values from papers
├── Normalize to 0-5 scale (enables comparison)
└── Build database with normalized scores

Week 2: DESCRIPTIVE ANALYSIS
├── Summary statistics (mean, median, SD)
├── Heatmaps showing patterns
├── Identify trends
└── Create tropism atlas

Week 3: STATISTICAL ANALYSIS
├── Calculate Cohen's d for pairwise comparisons
├── T-tests and ANOVA
├── Meta-analysis with random effects
├── Forest plots
└── Statistical inference

Week 4: MANUSCRIPT
├── Results use BOTH approaches:
│   ├── Descriptive: "AAV8 showed high liver tropism (4.65 ± 0.32)"
│   └── Inferential: "AAV8 was superior to AAV9 (d=1.23, p<0.001)"
└── Figures show BOTH:
    ├── Heatmaps (normalized scores)
    └── Forest plots (effect sizes)

    

## Step-by-Step Process

### Step 1: Get the Paper (5 minutes)

1. Go to: https://pubmed.ncbi.nlm.nih.gov/18432245/
2. Click "Full text links" → "PMC"
3. Download PDF or view online
4. Save PDF as: `data/raw/pdfs/18432245_Zincarelli_2008.pdf`

### Step 2: Identify the Data (5 minutes)

**Main data location:** Figure 2A

This figure shows:
- **Y-axis:** Vector genomes per μg DNA (log scale)
- **X-axis:** 9 tissues (Liver, Heart, Skeletal Muscle, Brain, Kidney, Lung, Pancreas, Spleen, Testis)
- **Bars:** 9 serotypes (AAV1-9)

### Step 3: Extract Values (30-45 minutes)

**Option A: Use WebPlotDigitizer (Recommended)**

1. Go to: https://automeris.io/WebPlotDigitizer/
2. Upload Figure 2A image
3. Select "2D (X-Y) Plot"
4. Define axes:
   - X-axis: 1-9 (tissues)
   - Y-axis: Log scale, 1e6 to 1e10
5. Click on each bar to extract value
6. Export as CSV

**Option B: Estimate from Figure**

If values are clear, estimate directly:
- Liver (AAV1): ~5×10⁹
- Brain (AAV1): ~1×10⁸
- etc.

### Step 4: Enter into Excel (45-60 minutes)

Open: `data/metadata/tropism_extraction_template.xlsx`

For each serotype-tissue combination, add a row:

paper_id: 1 pmid: 18432245 first_author: Zincarelli year: 2008 journal: Molecular Therapy serotype: AAV1 (then AAV2, AAV3, etc.) tissue: Liver (then Brain, Heart, etc.) species: Mouse administration_route: IV dose_vg_kg: 1e11 timepoint_days: 14 measurement_method: qPCR raw_value: [value from figure] units: vg/ug DNA normalized_score: [calculate or leave blank] quality_score: High notes: C57BL/6 mice, n=3-5 per group figure_reference: Figure 2A extraction_date: 2024-02-17

**Pro tip:** Copy-paste the repeated fields (pmid, author, year, etc.)

### Step 5: Normalize Values (10 minutes) using batch_normalize.py

For qPCR data (vg/ug DNA):

```python
import numpy as np

raw_value = 5.2e9  # Example
log_value = np.log10(raw_value)  # 9.716
normalized = (log_value - 6) / 4 * 5  # 4.64
normalized = np.clip(normalized, 0, 5)  # Ensure 0-5 range

### Step 5: Run the validate_extraction.py script to catch any erros and summarise all the data
