"""Generate preview chart images (map, trend, bar) + KPI numbers from the real data,
so we can show what the finished Tableau dashboard will look like."""
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUT = BASE / "mockup"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA / "obesity_dashboard_data.csv")
YEAR = 2022

# ---------- 1) MAP: obesity by state (2022, overall) ----------
m = df[(df.Metric == "Obesity") & (df.DemographicCategory == "Overall") &
       (df.Year == YEAR) & (~df.StateAbbr.isin(["US", "GU", "PR", "VI"]))]
fig = go.Figure(go.Choropleth(
    locations=m["StateAbbr"], z=m["Value"], locationmode="USA-states",
    colorscale="OrRd", colorbar_title="% obese",
    marker_line_color="white",
))
fig.update_layout(geo_scope="usa", margin=dict(l=0, r=0, t=0, b=0),
                  width=760, height=460)
fig.write_image(str(OUT / "map.png"), scale=2)

# ---------- 2) TREND: national obesity over time ----------
t = df[(df.Metric == "Obesity") & (df.DemographicCategory == "Overall") &
       (df.StateAbbr == "US")].sort_values("Year")
plt.figure(figsize=(6.2, 3.6))
plt.plot(t.Year, t.Value, marker="o", color="#c0392b", lw=2)
plt.fill_between(t.Year, t.Value, t.Value.min() - 1, alpha=0.08, color="#c0392b")
plt.title("National adult obesity rate over time", fontsize=12, loc="left")
plt.ylabel("% of adults"); plt.grid(alpha=0.25)
plt.tight_layout(); plt.savefig(OUT / "trend.png", dpi=150); plt.close()

# ---------- 3) BAR: obesity by income (national, 2022) ----------
b = df[(df.Metric == "Obesity") & (df.DemographicCategory == "Income") &
       (df.StateAbbr == "US") & (df.Year == YEAR)].copy()
b = b.groupby("DemographicGroup", as_index=False).Value.mean().sort_values("Value")
plt.figure(figsize=(6.2, 3.6))
colors = plt.cm.OrRd([0.4 + 0.5 * i / len(b) for i in range(len(b))])
plt.barh(b.DemographicGroup, b.Value, color=colors)
plt.title("Obesity by household income (2022)", fontsize=12, loc="left")
plt.xlabel("% of adults")
plt.tight_layout(); plt.savefig(OUT / "bar.png", dpi=150); plt.close()

# ---------- 4) KPI numbers ----------
nat = t[t.Year == YEAR].Value.iloc[0]
hi = m.loc[m.Value.idxmax()]
lo = m.loc[m.Value.idxmin()]
kpis = {
    "national": f"{nat:.1f}%",
    "highest": f"{hi.State} ({hi.Value:.1f}%)",
    "lowest": f"{lo.State} ({lo.Value:.1f}%)",
    "year": YEAR,
}
(OUT / "kpis.json").write_text(json.dumps(kpis, indent=2))
print("Charts saved to mockup/. KPIs:", kpis)
