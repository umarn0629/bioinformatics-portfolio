"""
Prepare CDC obesity/lifestyle data for a Tableau dashboard.
-----------------------------------------------------------
Takes the raw CDC BRFSS download and produces one clean, tidy CSV that
Tableau can read directly. We keep the 6 most useful health metrics and
give every column a plain-English name.

Source: CDC Nutrition, Physical Activity & Obesity (BRFSS), data.cdc.gov
Output: data/obesity_dashboard_data.csv
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

print("Loading raw data...")
df = pd.read_csv(DATA / "cdc_npao_raw.csv", low_memory=False)
print(f"  raw rows: {len(df):,}")

# --- Keep only the 6 health metrics we care about, with short friendly names ---
metric_map = {
    "Percent of adults aged 18 years and older who have obesity": "Obesity",
    "Percent of adults aged 18 years and older who have an overweight classification": "Overweight",
    "Percent of adults who engage in no leisure-time physical activity": "No Physical Activity",
    "Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)": "Meets Activity Guidelines",
    "Percent of adults who report consuming fruit less than one time daily": "Low Fruit Intake",
    "Percent of adults who report consuming vegetables less than one time daily": "Low Vegetable Intake",
}
df = df[df["question"].isin(metric_map)].copy()
df["Metric"] = df["question"].map(metric_map)

# --- Friendly names for the demographic breakdown ---
demo_map = {
    "OVR": "Overall", "AGEYR": "Age", "EDU": "Education",
    "INC": "Income", "RACE": "Race/Ethnicity", "SEX": "Sex",
}
df["DemographicCategory"] = df["stratificationcategoryid1"].map(demo_map)
df["DemographicGroup"] = df["stratification1"].fillna("Overall")

# --- Select + rename the columns we want to keep ---
clean = pd.DataFrame({
    "Year": df["yearstart"].astype(int),
    "State": df["locationdesc"],
    "StateAbbr": df["locationabbr"],
    "Metric": df["Metric"],
    "DemographicCategory": df["DemographicCategory"],
    "DemographicGroup": df["DemographicGroup"],
    "Value": pd.to_numeric(df["data_value"], errors="coerce"),
    "LowerCI": pd.to_numeric(df["low_confidence_limit"], errors="coerce"),
    "UpperCI": pd.to_numeric(df["high_confidence_limit"], errors="coerce"),
    "SampleSize": pd.to_numeric(df["sample_size"], errors="coerce"),
})

# --- Drop rows with no value (CDC suppresses some small samples) ---
clean = clean.dropna(subset=["Value", "DemographicCategory"])
clean = clean.sort_values(["Metric", "Year", "State"]).reset_index(drop=True)

out = DATA / "obesity_dashboard_data.csv"
clean.to_csv(out, index=False)

print(f"\nSaved clean file: {out.name}")
print(f"  clean rows: {len(clean):,}")
print(f"  years: {clean.Year.min()}–{clean.Year.max()}")
print(f"  metrics: {', '.join(sorted(clean.Metric.unique()))}")
print(f"  demographics: {', '.join(sorted(clean.DemographicCategory.unique()))}")
print("\nPreview:")
print(clean.head(6).to_string(index=False))
