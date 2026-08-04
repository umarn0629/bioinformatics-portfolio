"""
Lean Six Sigma DMAIC Case Study — Clinical Lab Specimen Processing
==================================================================
SIMULATED case study (not real lab data) demonstrating the DMAIC methodology
and Statistical Process Control (SPC) tooling in Python.

Scenario: A clinical lab has too many specimen defects (rejected/re-run samples)
and long, variable turnaround time (TAT). We use DMAIC to find root causes,
implement improvements, and prove the process is better and now in control.

Produces four figures: Pareto chart, fishbone diagram, X-bar/R control chart,
and a before/after process-capability comparison.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)   # reproducible simulation
BASE = Path(__file__).resolve().parent.parent
RESULTS = BASE / "results"; RESULTS.mkdir(exist_ok=True)

USL = 60.0   # spec: specimen turnaround time must be under 60 minutes

# ============================================================
# MEASURE — simulate baseline vs. post-improvement data
# ============================================================
DAYS, N = 30, 5          # 30 days each phase, subgroups of 5 specimens/day
# Baseline: higher, more variable TAT, with a couple of special-cause spikes
before = np.random.normal(52, 8, (DAYS, N))
before[7] += 18; before[19] += 15          # special-cause events
# After improvement: lower and tighter TAT
after = np.random.normal(44, 4, (DAYS, N))

# Defect counts by type over the baseline period (for the Pareto)
defects = {
    "Mislabeled specimen": 45, "Hemolyzed sample": 32, "Insufficient volume": 18,
    "Clotted specimen": 12, "Wrong tube type": 8, "Other": 5,
}

# ============================================================
# ANALYZE — Figure 1: Pareto chart of defect types
# ============================================================
d = pd.Series(defects).sort_values(ascending=False)
cum = d.cumsum() / d.sum() * 100
fig, ax1 = plt.subplots(figsize=(9, 5.5))
ax1.bar(d.index, d.values, color="#4c72b0")
ax1.set_ylabel("Number of defects"); ax1.set_title("Pareto Chart — Specimen Processing Defects")
ax1.tick_params(axis="x", rotation=25)
ax2 = ax1.twinx()
ax2.plot(d.index, cum.values, color="#c44e52", marker="o")
ax2.axhline(80, ls="--", color="gray"); ax2.set_ylabel("Cumulative %")
ax2.set_ylim(0, 105)
for i, v in enumerate(cum.values):
    ax2.text(i, v + 2, f"{v:.0f}%", ha="center", fontsize=8, color="#c44e52")
fig.tight_layout(); fig.savefig(RESULTS / "1_pareto_chart.png", dpi=150); plt.close()
print("saved 1_pareto_chart.png")
top2 = cum.iloc[1]
print(f"  Top 2 defect types account for {top2:.0f}% of all defects.")

# ============================================================
# ANALYZE — Figure 2: Fishbone (Ishikawa) diagram
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6.5)); ax.axis("off")
ax.set_xlim(0, 12); ax.set_ylim(0, 8)
# spine + effect
ax.annotate("", xy=(10, 4), xytext=(1, 4), arrowprops=dict(arrowstyle="-|>", lw=2))
ax.text(10.1, 4, "Specimen\ndefects &\nlong TAT", va="center", fontsize=11,
        bbox=dict(boxstyle="round", fc="#ffe6e6", ec="#c44e52"))
categories = {
    "People": ["Inadequate training", "Staff turnover", "Rushing at peak hours"],
    "Method": ["Unclear labeling SOP", "Manual data entry"],
    "Machine": ["Centrifuge drift", "Analyzer downtime"],
    "Material": ["Low-quality tubes", "Expired reagents"],
    "Measurement": ["No barcode check", "Inconsistent volume QC"],
    "Environment": ["High workload", "Crowded workspace"],
}
tops = list(categories.items())[:3]; bots = list(categories.items())[3:]
def draw_bone(x_spine, cat, causes, up):
    y0 = 4; y1 = 7 if up else 1; x1 = x_spine - 1.4
    ax.plot([x_spine, x1], [y0, y1], color="#333", lw=1.5)
    ax.text(x1 - 0.1, y1 + (0.2 if up else -0.4), cat, fontweight="bold", fontsize=10,
            ha="center", color="#4c72b0")
    for k, c in enumerate(causes):
        yy = y1 + (-0.7 - 0.6 * k if up else 0.7 + 0.6 * k)
        xx = x1 + 0.35 + 0.25 * k
        ax.text(xx, yy, f"– {c}", fontsize=8, va="center")
for i, (cat, causes) in enumerate(tops):
    draw_bone(3 + i * 2.4, cat, causes, up=True)
for i, (cat, causes) in enumerate(bots):
    draw_bone(3 + i * 2.4, cat, causes, up=False)
ax.set_title("Fishbone (Ishikawa) Root-Cause Analysis", fontsize=13)
fig.tight_layout(); fig.savefig(RESULTS / "2_fishbone_diagram.png", dpi=150); plt.close()
print("saved 2_fishbone_diagram.png")

# ============================================================
# CONTROL — Figure 3: X-bar and R control charts
# ============================================================
# SPC constants for subgroup size n=5
A2, D3, D4 = 0.577, 0.0, 2.114
def xbar_r(data):
    xbar = data.mean(axis=1); R = data.max(axis=1) - data.min(axis=1)
    return xbar, R
xb_b, R_b = xbar_r(before); xb_a, R_a = xbar_r(after)
# Control limits established from the BASELINE phase
Xbb = xb_b.mean(); Rb = R_b.mean()
UCLx, LCLx = Xbb + A2 * Rb, Xbb - A2 * Rb
UCLr, LCLr = D4 * Rb, D3 * Rb

fig, (axx, axr) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
x_all = np.arange(2 * DAYS)
xb_all = np.concatenate([xb_b, xb_a]); R_all = np.concatenate([R_b, R_a])
# X-bar chart
axx.plot(x_all, xb_all, marker="o", color="#333")
axx.axhline(Xbb, color="green"); axx.axhline(UCLx, color="red", ls="--"); axx.axhline(LCLx, color="red", ls="--")
axx.axvline(DAYS - 0.5, color="blue", ls=":");
axx.text(DAYS - 0.5, axx.get_ylim()[1], " Improvement", color="blue", va="top")
oob = x_all[(xb_all > UCLx)]
axx.scatter(oob, xb_all[oob.astype(int)], color="red", zorder=5, s=80, label="Out of control")
axx.set_ylabel("Mean TAT (min)"); axx.set_title("X-bar Chart — specimen turnaround time")
axx.text(1, UCLx, "UCL", color="red", va="bottom"); axx.text(1, Xbb, "CL", color="green", va="bottom")
axx.legend(loc="upper right")
# R chart
axr.plot(x_all, R_all, marker="o", color="#333")
axr.axhline(Rb, color="green"); axr.axhline(UCLr, color="red", ls="--"); axr.axhline(LCLr, color="red", ls="--")
axr.axvline(DAYS - 0.5, color="blue", ls=":")
axr.set_ylabel("Range (min)"); axr.set_xlabel("Day"); axr.set_title("R Chart — within-day variation")
fig.tight_layout(); fig.savefig(RESULTS / "3_control_chart.png", dpi=150); plt.close()
print("saved 3_control_chart.png")

# ============================================================
# CONTROL — Figure 4: process capability before vs. after
# ============================================================
def cpk_upper(data):  # only an upper spec limit here
    mu, sd = data.mean(), data.std(ddof=1)
    return (USL - mu) / (3 * sd), mu, sd
cpk_b, mu_b, sd_b = cpk_upper(before); cpk_a, mu_a, sd_a = cpk_upper(after)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, data, mu, sd, cpk, ttl, col in [
    (a1, before, mu_b, sd_b, cpk_b, "Before improvement", "#c44e52"),
    (a2, after, mu_a, sd_a, cpk_a, "After improvement", "#55a868")]:
    ax.hist(data.flatten(), bins=15, color=col, alpha=.7, edgecolor="white")
    ax.axvline(USL, color="black", ls="--"); ax.text(USL, ax.get_ylim()[1]*.9, " USL=60", fontsize=9)
    ax.set_title(f"{ttl}\nmean={mu:.1f}, Cpk={cpk:.2f}"); ax.set_xlabel("TAT (min)")
a1.set_ylabel("Frequency")
fig.suptitle("Process Capability — turnaround time (USL = 60 min)", y=1.03, fontsize=13)
fig.tight_layout(); fig.savefig(RESULTS / "4_capability.png", dpi=150, bbox_inches="tight"); plt.close()
print("saved 4_capability.png")

# ============================================================
# Summary
# ============================================================
defect_rate_before = 6.0; defect_rate_after = 1.8   # simulated program outcome
print("\n" + "=" * 58)
print("DMAIC RESULTS (simulated case study)")
print("=" * 58)
print(f"  Mean turnaround time:  {mu_b:.1f} -> {mu_a:.1f} min")
print(f"  Process capability Cpk: {cpk_b:.2f} -> {cpk_a:.2f}")
print(f"  Defect rate:           {defect_rate_before:.1f}% -> {defect_rate_after:.1f}%")
print(f"  Top 2 defects drove {top2:.0f}% of problems (Pareto focus).")
print("=" * 58)
