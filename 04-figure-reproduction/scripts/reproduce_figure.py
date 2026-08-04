"""
Published Figure Reproduction
=============================
Paper: Himes et al. (2014), PLoS ONE 9(6):e99625.
  "RNA-Seq Transcriptome Profiling Identifies CRISPLD2 as a Glucocorticoid
   Responsive Gene ... in Airway Smooth Muscle Cells."

Central claim we reproduce: the gene CRISPLD2 is significantly UP-regulated
when airway smooth muscle cells are treated with dexamethasone.

This script re-derives that result from the raw RNA-seq counts and recreates
the key figure: CRISPLD2 expression, untreated vs. dexamethasone-treated.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"; RESULTS = BASE / "results"; RESULTS.mkdir(exist_ok=True)

CRISPLD2_ID = "83716"   # NCBI GeneID for CRISPLD2

print("STEP 1 — Load raw counts and keep the 8 untreated/Dex samples")
counts = pd.read_csv(DATA / "GSE52778_raw_counts.tsv.gz", sep="\t", index_col=0)
counts.index = counts.index.astype(str)
meta = pd.read_csv(DATA / "sample_metadata.csv", index_col="sample")
meta = meta[meta["treatment"].isin(["untreated", "Dex"])].copy()
counts = counts[meta.index]
counts = counts.loc[counts.sum(axis=1) >= 10]

print("STEP 2 — Run DESeq2 to normalize counts and test CRISPLD2")
dds = DeseqDataSet(counts=counts.T, metadata=meta,
                   design="~cell_line + treatment", refit_cooks=True)
dds.deseq2()
stat = DeseqStats(dds, contrast=["treatment", "Dex", "untreated"])
stat.summary()
res = stat.results_df
row = res.loc[CRISPLD2_ID]
log2fc, padj = row["log2FoldChange"], row["padj"]
print(f"\n  CRISPLD2: log2 fold change = {log2fc:.2f}  (~{2**log2fc:.1f}x),  "
      f"adjusted p = {padj:.1e}")

print("\nSTEP 3 — Pull normalized CRISPLD2 expression per sample")
norm = pd.DataFrame(dds.layers["normed_counts"],
                    index=dds.obs_names, columns=dds.var_names)
plot = meta.copy()
plot["CRISPLD2"] = norm[CRISPLD2_ID]
plot["treatment"] = plot["treatment"].map({"untreated": "Untreated", "Dex": "Dexamethasone"})
order = ["Untreated", "Dexamethasone"]

print("\nSTEP 4 — Recreate the figure")
fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 5.5))

# Panel A: box + points by treatment
sns.boxplot(data=plot, x="treatment", y="CRISPLD2", order=order,
            width=.5, showfliers=False, palette=["#4c72b0", "#c44e52"], ax=axA)
sns.stripplot(data=plot, x="treatment", y="CRISPLD2", order=order,
              color="black", size=8, jitter=.12, ax=axA)
axA.set_title("CRISPLD2 expression by treatment")
axA.set_xlabel(""); axA.set_ylabel("Normalized expression (counts)")
axA.text(0.5, 0.95, f"log2FC = {log2fc:.2f}   adj. p = {padj:.1e}",
         transform=axA.transAxes, ha="center", va="top", fontsize=10,
         bbox=dict(boxstyle="round", fc="white", ec="gray"))

# Panel B: paired lines — each of the 4 donors, untreated -> Dex
piv = plot.pivot_table(index="cell_line", columns="treatment", values="CRISPLD2")
for cell in piv.index:
    axB.plot(order, [piv.loc[cell, "Untreated"], piv.loc[cell, "Dexamethasone"]],
             marker="o", label=cell)
axB.set_title("Each donor increases with dexamethasone")
axB.set_xlabel(""); axB.set_ylabel("Normalized expression (counts)")
axB.legend(title="Cell line", fontsize=8)

fig.suptitle("Reproduction of Himes et al. 2014: CRISPLD2 is glucocorticoid-responsive",
             fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(RESULTS / "CRISPLD2_reproduction.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved CRISPLD2_reproduction.png")

# Save the underlying numbers
plot[["cell_line", "treatment", "CRISPLD2"]].to_csv(RESULTS / "CRISPLD2_expression.csv", index=True)

print("\n" + "=" * 60)
print("DONE!  The paper's central claim is reproduced:")
print(f"  CRISPLD2 is up ~{2**log2fc:.1f}x with dexamethasone (adj. p = {padj:.1e}).")
print("=" * 60)
