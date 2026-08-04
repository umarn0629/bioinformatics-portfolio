# Lean Six Sigma DMAIC Case Study — Clinical Lab Specimen Processing

A process-improvement case study demonstrating the **DMAIC** methodology and
**Statistical Process Control (SPC)** using Python.

> **Note:** This uses a **simulated** dataset (a realistic case study), not real
> lab data. It demonstrates the Six Sigma methodology, SPC math, and analysis
> tooling — the skills, not a specific workplace outcome.

## Scenario
A clinical lab has too many specimen defects (rejected / re-run samples) and long,
variable turnaround time (TAT). Goal: cut the defect rate and stabilize TAT below
the 60-minute upper spec limit.

## DMAIC walkthrough
- **Define** — Problem: high defect rate + unstable TAT. Goal: reduce both.
- **Measure** — Baseline TAT (subgroups of 5/day for 30 days) and defect counts by type.
- **Analyze** —
  - *Pareto chart:* the top 2 defect types (mislabeling, hemolysis) drive **64%** of defects.
  - *Fishbone (Ishikawa):* root causes across People / Method / Machine / Material / Measurement / Environment.
- **Improve** — Corrective actions targeting the top causes (barcode labeling system,
  staff retraining, centrifuge preventive-maintenance schedule, standardized volume SOP).
- **Control** — X-bar / R control charts confirm the process is stable and improved;
  process-capability (Cpk) recomputed.

## Results (simulated)
| Metric | Before | After |
|---|---|---|
| Mean turnaround time | 52.4 min | 44.3 min |
| Process capability (Cpk) | 0.31 | 1.28 |
| Defect rate | 6.0% | 1.8% |

## Figures (in `results/`)
1. `1_pareto_chart.png` — defect types (80/20)
2. `2_fishbone_diagram.png` — root-cause analysis
3. `3_control_chart.png` — X-bar & R charts, before vs. after
4. `4_capability.png` — process capability vs. the 60-min spec limit

## How to run
```bash
conda activate bioinfo
python scripts/dmaic_analysis.py
```

## Tools
Python, pandas, numpy, matplotlib · Lean Six Sigma (DMAIC, Pareto, Ishikawa, SPC, Cpk)
