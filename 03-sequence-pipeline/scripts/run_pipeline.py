"""
Bioinformatics Sequence Analysis Pipeline
=========================================
Question: How closely related are different animal species, based on the
beta-hemoglobin protein they all share?

This pipeline:
  1. FETCHES the beta-hemoglobin (HBB) protein sequence for 9 species from NCBI.
  2. ALIGNS every pair of sequences and measures how similar they are.
  3. BUILDS a phylogenetic (evolutionary) tree from those similarities.
  4. VISUALIZES the result as a similarity heatmap and a tree.

Everything runs in Python with Biopython. You run it once; read the comments
to understand each step (that's what lets you explain it in an interview).
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from Bio import Entrez, SeqIO, Phylo
from Bio.Align import PairwiseAligner, substitution_matrices
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

Entrez.email = "umarn0629@gmail.com"   # NCBI asks who is making requests

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"; RESULTS = BASE / "results"
RESULTS.mkdir(exist_ok=True)

# One verified beta-hemoglobin protein per species (stable NCBI accessions).
ACCESSIONS = {
    "Human":       "NP_000509.1",
    "Chimpanzee":  "XP_508242.1",
    "Mouse":       "NP_001188320.1",
    "Rat":         "NP_150237.1",
    "Cow":         "NP_776342.1",
    "Dog":         "NP_001257812.1",
    "Chicken":     "NP_990820.1",
    "Frog":        "NP_988859.1",
    "Zebrafish":   "NP_571095.1",
}

# ---------------------------------------------------------------
print("STEP 1 — Fetching sequences from NCBI")
# ---------------------------------------------------------------
fasta_path = DATA / "hemoglobin_sequences.fasta"
if fasta_path.exists():
    records = {r.id: r for r in SeqIO.parse(fasta_path, "fasta")}
    print(f"  loaded {len(records)} cached sequences from {fasta_path.name}")
else:
    acc_to_species = {v.split(".")[0]: k for k, v in ACCESSIONS.items()}
    handle = Entrez.efetch(db="protein", id=",".join(ACCESSIONS.values()),
                           rettype="fasta", retmode="text")
    fetched = list(SeqIO.parse(handle, "fasta")); handle.close()
    records = {}
    for rec in fetched:
        species = acc_to_species[rec.id.split(".")[0]]
        rec.id = species; rec.name = species
        rec.description = f"{species}|{rec.description}"
        records[species] = rec
    SeqIO.write(list(records.values()), fasta_path, "fasta")
    print(f"  fetched {len(records)} sequences and saved to {fasta_path.name}")

species_list = list(ACCESSIONS.keys())
for sp in species_list:
    print(f"    {sp:12s} {len(records[sp].seq)} amino acids")

# ---------------------------------------------------------------
print("\nSTEP 2 — Comparing every pair of sequences (% identity)")
# ---------------------------------------------------------------
# A protein aligner scored with BLOSUM62 (the standard protein scoring matrix).
aligner = PairwiseAligner()
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
aligner.open_gap_score = -10
aligner.extend_gap_score = -0.5

def percent_identity(seq_a, seq_b):
    """Align two proteins and return the % of positions that are identical."""
    aln = aligner.align(seq_a, seq_b)[0]
    a_str, b_str = str(aln[0]), str(aln[1])      # aligned strings (with gaps)
    matches = sum(1 for x, y in zip(a_str, b_str) if x == y and x != "-")
    return 100.0 * matches / len(a_str)

n = len(species_list)
ident = pd.DataFrame(np.zeros((n, n)), index=species_list, columns=species_list)
for i, a in enumerate(species_list):
    for j, b in enumerate(species_list):
        if i <= j:
            pid = 100.0 if i == j else percent_identity(records[a].seq, records[b].seq)
            ident.loc[a, b] = pid
            ident.loc[b, a] = pid
ident.to_csv(RESULTS / "percent_identity_matrix.csv")

# Show how similar each species is to humans.
human_sim = ident["Human"].drop("Human").sort_values(ascending=False)
print("  % identity to HUMAN hemoglobin:")
for sp, v in human_sim.items():
    print(f"    {sp:12s} {v:5.1f}%")

# ---------------------------------------------------------------
print("\nSTEP 3 — Building the phylogenetic (evolutionary) tree")
# ---------------------------------------------------------------
# Distance = how different two proteins are (100% - % identical).
# Biopython builds a Neighbor-Joining tree from a lower-triangular distance matrix.
lower = []
for i, a in enumerate(species_list):
    lower.append([round((100.0 - ident.loc[a, species_list[j]]) / 100.0, 4)
                  for j in range(i + 1)])
dm = DistanceMatrix(names=species_list, matrix=lower)
tree = DistanceTreeConstructor().nj(dm)
tree.ladderize()
# clean up internal node labels so the drawing isn't cluttered
for clade in tree.get_nonterminals():
    clade.name = None
Phylo.write(tree, RESULTS / "phylogenetic_tree.newick", "newick")

# ---------------------------------------------------------------
print("\nSTEP 4 — Making the figures")
# ---------------------------------------------------------------
# Heatmap of similarity
plt.figure(figsize=(9, 7.5))
sns.heatmap(ident, annot=True, fmt=".0f", cmap="YlGnBu", vmin=40, vmax=100,
            cbar_kws={"label": "% identical"}, linewidths=.5)
plt.title("Beta-hemoglobin similarity between species (%)")
plt.tight_layout(); plt.savefig(RESULTS / "similarity_heatmap.png", dpi=150); plt.close()
print("  saved similarity_heatmap.png")

# Phylogenetic tree
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(1, 1, 1)
Phylo.draw(tree, axes=ax, do_show=False, branch_labels=None)
ax.set_title("Phylogenetic tree from beta-hemoglobin (Neighbor-Joining)")
ax.set_xlabel("evolutionary distance"); ax.set_ylabel("")
ax.set_yticks([])   # hide the meaningless row numbers on the left
plt.tight_layout(); plt.savefig(RESULTS / "phylogenetic_tree.png", dpi=150); plt.close()
print("  saved phylogenetic_tree.png")

print("\n" + "=" * 55)
print("DONE!  See the 'results' folder for the heatmap, tree, and tables.")
print("=" * 55)
