"""
Differential Gene Expression Analysis  —  GSE52778 (the "airway" study)
======================================================================
Question: Which genes change when human airway smooth muscle cells are
treated with dexamethasone (an asthma steroid) vs. left untreated?

This script:
  1. Loads the raw RNA-seq count data downloaded from NCBI GEO.
  2. Keeps only the 8 samples we're comparing (4 untreated, 4 dexamethasone).
  3. Runs DESeq2 (via pydeseq2) to find differentially expressed genes,
     while controlling for which cell line each sample came from.
  4. Adds human-readable gene names.
  5. Saves a results table + three figures (volcano, heatmap, PCA).

You run this once. Read the comments to understand each step — that's what
lets you explain the project in an interview.
"""

# ---- Standard data tools ----
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ---- The bioinformatics engine (DESeq2, in Python) ----
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# ---- Where things live ----
BASE = Path(__file__).resolve().parent.parent      # the 01-gene-expression folder
DATA = BASE / "data"
RESULTS = BASE / "results"
RESULTS.mkdir(exist_ok=True)

print("=" * 60)
print("STEP 1 — Loading the data")
print("=" * 60)

# The count matrix: rows = genes (by NCBI GeneID), columns = samples.
counts = pd.read_csv(DATA / "GSE52778_raw_counts.tsv.gz", sep="\t", index_col=0)
counts.index = counts.index.astype(str)            # GeneIDs as text labels
print(f"Loaded counts: {counts.shape[0]:,} genes x {counts.shape[1]} samples")

# The metadata: which sample is which cell line + treatment.
meta = pd.read_csv(DATA / "sample_metadata.csv", index_col="sample")

# Keep ONLY untreated vs. Dex (the classic comparison) -> 8 samples.
meta = meta[meta["treatment"].isin(["untreated", "Dex"])].copy()
counts = counts[meta.index]                          # same 8 samples, same order
print(f"Comparing {(meta.treatment=='Dex').sum()} Dex vs "
      f"{(meta.treatment=='untreated').sum()} untreated samples")

print("\n" + "=" * 60)
print("STEP 2 — Cleaning: drop genes with almost no reads")
print("=" * 60)
# DESeq2 works best if we remove genes that are barely detected.
# Keep a gene only if it has at least 10 total reads across all samples.
keep = counts.sum(axis=1) >= 10
counts = counts.loc[keep]
print(f"Kept {counts.shape[0]:,} genes with >=10 total reads")

print("\n" + "=" * 60)
print("STEP 3 — Running DESeq2")
print("=" * 60)
# pydeseq2 wants samples as ROWS and genes as COLUMNS, so we transpose (.T).
# design "~cell_line + treatment" tells it: account for cell-line differences,
# then test the effect of treatment.
dds = DeseqDataSet(
    counts=counts.T,
    metadata=meta,
    design="~cell_line + treatment",
    refit_cooks=True,
)
dds.deseq2()   # <- this does the statistical modeling

# Compute the specific comparison: Dexamethasone vs. untreated.
stat = DeseqStats(dds, contrast=["treatment", "Dex", "untreated"])
stat.summary()
res = stat.results_df.copy()

print("\n" + "=" * 60)
print("STEP 4 — Adding human-readable gene names")
print("=" * 60)
# The data uses numeric GeneIDs. Look up the real gene symbols (e.g. "DUSP1").
try:
    import mygene
    mg = mygene.MyGeneInfo()
    info = mg.querymany(res.index.tolist(), scopes="entrezgene",
                        fields="symbol", species="human",
                        as_dataframe=True, verbose=False)
    res["symbol"] = info["symbol"].reindex(res.index)
    res["symbol"] = res["symbol"].fillna(res.index.to_series())
    print("Gene symbols added.")
except Exception as e:
    print(f"(Could not fetch symbols, using GeneIDs instead: {e})")
    res["symbol"] = res.index.to_series()

# Sort so the most statistically significant genes are at the top.
res = res.sort_values("padj")
res.to_csv(RESULTS / "differential_expression_results.csv")

# How many genes are significantly changed? (padj < 0.05 is the usual cutoff)
sig = res[res["padj"] < 0.05]
up = sig[sig["log2FoldChange"] > 0]
down = sig[sig["log2FoldChange"] < 0]
print(f"\nSignificant genes (padj < 0.05): {len(sig):,}")
print(f"   up in Dex:   {len(up):,}")
print(f"   down in Dex: {len(down):,}")
print("\nTop 10 most significant genes:")
print(res[["symbol", "log2FoldChange", "padj"]].head(10).to_string())

print("\n" + "=" * 60)
print("STEP 5 — Making the figures")
print("=" * 60)

# ---------- FIGURE 1: Volcano plot ----------
# x-axis = how much a gene changed; y-axis = how confident we are.
# Genes in the top corners are the strongest, most reliable hits.
plot_df = res.dropna(subset=["padj", "log2FoldChange"]).copy()
plot_df["neglog10padj"] = -np.log10(plot_df["padj"].clip(lower=1e-300))
plot_df["significant"] = (plot_df["padj"] < 0.05) & (plot_df["log2FoldChange"].abs() > 1)

plt.figure(figsize=(8, 6))
plt.scatter(plot_df.loc[~plot_df.significant, "log2FoldChange"],
            plot_df.loc[~plot_df.significant, "neglog10padj"],
            s=6, c="lightgray", label="Not significant")
plt.scatter(plot_df.loc[plot_df.significant, "log2FoldChange"],
            plot_df.loc[plot_df.significant, "neglog10padj"],
            s=8, c="crimson", label="Significant")
# Label the 10 strongest genes.
for _, r in plot_df.nlargest(10, "neglog10padj").iterrows():
    plt.text(r["log2FoldChange"], r["neglog10padj"], r["symbol"], fontsize=8)
plt.axvline(-1, ls="--", c="gray", lw=0.7); plt.axvline(1, ls="--", c="gray", lw=0.7)
plt.axhline(-np.log10(0.05), ls="--", c="gray", lw=0.7)
plt.xlabel("log2 fold change  (Dex vs untreated)")
plt.ylabel("-log10 adjusted p-value")
plt.title("Volcano plot: genes changed by dexamethasone")
plt.legend(); plt.tight_layout()
plt.savefig(RESULTS / "volcano_plot.png", dpi=150)
plt.close()
print("Saved volcano_plot.png")

# ---------- FIGURE 2: Heatmap of the top 30 genes ----------
# Shows the expression pattern of the strongest genes across all 8 samples.
norm = pd.DataFrame(dds.layers["normed_counts"],
                    index=dds.obs_names, columns=dds.var_names)
top_ids = sig.head(30).index
mat = np.log2(norm[top_ids] + 1).T                 # genes x samples, log scale
zmat = mat.sub(mat.mean(axis=1), axis=0).div(mat.std(axis=1) + 1e-9, axis=0)  # z-score
zmat.index = res.loc[top_ids, "symbol"].values     # label rows with gene names
col_colors = meta.loc[zmat.columns, "treatment"].map(
    {"Dex": "crimson", "untreated": "steelblue"})
g = sns.clustermap(zmat, cmap="RdBu_r", center=0, figsize=(9, 10),
                   col_colors=col_colors, xticklabels=True, yticklabels=True)
g.fig.suptitle("Top 30 differentially expressed genes", y=1.01)
g.savefig(RESULTS / "heatmap_top_genes.png", dpi=150)
plt.close()
print("Saved heatmap_top_genes.png")

# ---------- FIGURE 3: PCA (samples overview) ----------
# A sanity check: do treated and untreated samples separate cleanly?
from sklearn.decomposition import PCA
X = np.log2(norm + 1).values
X = X[:, X.std(axis=0) > 0]
pcs = PCA(n_components=2).fit_transform(
    (X - X.mean(axis=0)) / X.std(axis=0))
plt.figure(figsize=(7, 6))
for grp, color in {"Dex": "crimson", "untreated": "steelblue"}.items():
    idx = (meta["treatment"] == grp).values
    plt.scatter(pcs[idx, 0], pcs[idx, 1], c=color, s=80, label=grp)
plt.xlabel("PC1"); plt.ylabel("PC2")
plt.title("PCA: do the two groups separate?")
plt.legend(); plt.tight_layout()
plt.savefig(RESULTS / "pca_plot.png", dpi=150)
plt.close()
print("Saved pca_plot.png")

print("\n" + "=" * 60)
print("DONE!  Check the 'results' folder for your table and 3 figures.")
print("=" * 60)
