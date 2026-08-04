# Published Figure Reproduction — CRISPLD2 (Himes et al. 2014)

Reproducing the central finding of a peer-reviewed paper from its raw public data.

## The paper
Himes BE, et al. (2014). *RNA-Seq Transcriptome Profiling Identifies CRISPLD2 as a
Glucocorticoid Responsive Gene that Modulates Cytokine Function in Airway Smooth
Muscle Cells.* **PLoS ONE 9(6): e99625.** (Data: NCBI GEO GSE52778.)

**Claim reproduced:** CRISPLD2 is significantly **up-regulated** in airway smooth
muscle cells treated with **dexamethasone** (a glucocorticoid).

## What this does
1. Loads the raw RNA-seq counts (untreated vs. dexamethasone, 4 donors).
2. Runs DESeq2 to normalize and test the CRISPLD2 gene.
3. Recreates the key figure showing CRISPLD2 expression by treatment.

## Result (matches the paper)
- **CRISPLD2 log2 fold change = +2.63 (~6.2× higher with dexamethasone)**
- **Adjusted p-value = 2.2 × 10⁻⁶⁰**
- All 4 donor cell lines show the increase (see paired plot).

## Figure (in `results/`)
- `CRISPLD2_reproduction.png` — left: expression by treatment with stats;
  right: each donor's increase from untreated → dexamethasone
- `CRISPLD2_expression.csv` — the underlying per-sample values

## How to run
```bash
conda activate bioinfo
python scripts/reproduce_figure.py
```

## Why this matters
This demonstrates the ability to read a primary scientific paper, locate its central
claim, obtain the underlying public data, and independently verify the result in code —
a core skill in computational biology and reproducible research.

## Tools
Python, DESeq2 (pydeseq2), pandas, matplotlib, seaborn
