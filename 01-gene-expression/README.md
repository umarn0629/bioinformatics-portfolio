# Differential Gene Expression Analysis — Dexamethasone in Airway Cells

**Question:** Which genes change when human airway smooth muscle cells are treated
with dexamethasone (a glucocorticoid steroid used to treat asthma) vs. untreated?

## Data
- **Source:** NCBI GEO, accession **GSE52778** (the "airway" study)
- **Samples:** 8 RNA-seq samples — 4 dexamethasone-treated, 4 untreated, from 4 human donors
- **Type:** Raw RNA-seq read counts (NCBI-generated), ~21,800 genes after filtering

## Method
1. Loaded raw counts and removed genes with fewer than 10 total reads.
2. Ran **DESeq2** (via `pydeseq2`) with the design `~ cell_line + treatment`, which
   controls for donor-to-donor variation before testing the effect of treatment.
3. Compared **Dexamethasone vs. untreated** and mapped NCBI GeneIDs to gene symbols.
4. Visualized results with a volcano plot, clustered heatmap, and PCA.

## Results
- **4,536 genes** significantly differentially expressed (adjusted p < 0.05):
  **2,489 up**, **2,047 down** in dexamethasone-treated cells.
- Top hits include well-known glucocorticoid-response genes: **DUSP1, KLF15, SPARCL1,
  PER1, SERPINA3, GPX3** — confirming the analysis captures real biology.
- PCA and heatmap show clean separation between treated and untreated samples.

## Figures (in `results/`)
- `volcano_plot.png` — significance vs. fold change, top genes labeled
- `heatmap_top_genes.png` — expression of the top 30 genes across all 8 samples
- `pca_plot.png` — sample-level overview showing the two groups separate

## How to run
```bash
conda activate bioinfo
python scripts/run_analysis.py
```

## Tools
Python, pandas, DESeq2 (pydeseq2), matplotlib, seaborn, scikit-learn, mygene
