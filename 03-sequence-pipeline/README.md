# Bioinformatics Sequence Analysis Pipeline — Hemoglobin Across Species

**Question:** How closely related are different animal species, based on the
beta-hemoglobin protein they all share?

## What it does
An automated Biopython pipeline that:
1. **Fetches** the beta-hemoglobin (HBB) protein sequence for **9 species** directly
   from **NCBI** (human, chimpanzee, mouse, rat, cow, dog, chicken, frog, zebrafish).
2. **Aligns** every pair of sequences (BLOSUM62 scoring) and computes **% identity**.
3. **Builds** a phylogenetic tree using the Neighbor-Joining method.
4. **Visualizes** a similarity heatmap and the evolutionary tree.

## Key results
- **Human and chimpanzee beta-hemoglobin are 100% identical** — no amino-acid differences.
- Similarity to human hemoglobin tracks evolutionary distance:
  Dog 90% · Cow 84% · Rat 82% · Mouse 80% · Chicken 69% · Zebrafish 51% · Frog 42%.
- The tree correctly groups **primates**, then other **mammals**, with **chicken**,
  then **fish/amphibian** branching off earlier — matching known vertebrate evolution.

## Figures (in `results/`)
- `similarity_heatmap.png` — % identity between all 9 species
- `phylogenetic_tree.png` — Neighbor-Joining evolutionary tree
- `percent_identity_matrix.csv` — the numbers behind the heatmap
- `phylogenetic_tree.newick` — the tree in standard Newick format
- `hemoglobin_sequences.fasta` — the sequences fetched from NCBI (cached)

## How to run
```bash
conda activate bioinfo
python scripts/run_pipeline.py
```
(First run downloads from NCBI; later runs reuse the cached FASTA file.)

## Tools
Python, Biopython (Entrez, PairwiseAligner, Phylo), pandas, matplotlib, seaborn

## Method note
Distances come from pairwise global alignments (BLOSUM62) rather than a full
multiple-sequence alignment, so the tree is a fast approximation — but it recovers
the expected vertebrate relationships.
