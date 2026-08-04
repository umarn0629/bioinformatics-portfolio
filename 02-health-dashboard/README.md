# U.S. Adult Obesity & Lifestyle Dashboard (CDC BRFSS, 2011–2024)

An interactive Tableau dashboard exploring adult obesity, physical activity, and
nutrition across U.S. states, over time, and by demographic group.

- **Data source:** CDC Nutrition, Physical Activity & Obesity (BRFSS), data.cdc.gov
- **Clean dataset:** `data/obesity_dashboard_data.csv` (73,504 rows)
- **Tool:** Tableau Public (free)
- **Live dashboard:** [add your Tableau Public link here after publishing]

---

## The data, in plain terms
Each row = one health statistic for one **state**, one **year**, one **metric**,
and one **group of people**. Columns:

| Column | Meaning |
|---|---|
| Year | 2011–2024 |
| State / StateAbbr | U.S. state (plus "National") |
| Metric | Obesity, Overweight, No Physical Activity, Meets Activity Guidelines, Low Fruit Intake, Low Vegetable Intake |
| DemographicCategory | Overall, Age, Education, Income, Race/Ethnicity, Sex |
| DemographicGroup | the specific group (e.g. "$75,000 or greater") — "Overall" when not broken down |
| Value | the percentage (this is what you chart) |
| LowerCI / UpperCI | confidence interval |
| SampleSize | number of people surveyed |

### ⭐ THE GOLDEN RULE (read this twice)
Because every row is a *different* metric/group, you must always tell each chart
exactly what to show, or Tableau will add unrelated numbers together. On **every**
sheet you build:
1. Filter **Metric** to ONE value (e.g. Obesity).
2. Filter **DemographicCategory** appropriately (usually "Overall").
3. Set the **Value** measure to **Average** (not Sum).

To set Average: right-click the green `Value` pill → Measure → Average.

---

## What you'll build (4 panels)
1. **Map** — obesity rate by state (color-coded)
2. **Trend line** — a metric over time, nationally
3. **Bar chart** — a metric broken down by demographic group (shows disparities)
4. **KPI numbers** — national rate, plus highest/lowest state

---

## PART 1 — Install Tableau Public (one time)
1. Go to **public.tableau.com** and click **Download the App** (or "Sign up" — it's free, no payment).
2. Install it like any Mac app, then open **Tableau Public**.
3. Create a free Tableau Public account when prompted (you'll need it to publish).

## PART 2 — Load your data
1. In Tableau, left side → **Connect → To a File → Text file**.
2. Choose `~/Desktop/bioinformatics-projects/02-health-dashboard/data/obesity_dashboard_data.csv`.
3. You'll see the data preview. Bottom-left, click **Sheet 1** to start building.
4. Tableau should show a small globe 🌐 next to **State** — that means it recognized
   it as a map location. (If not: right-click State → Geographic Role → State/Province.)

## PART 3 — Build each sheet

### Sheet 1 → "Obesity Map"
1. Double-click **State**. A map appears with dots.
2. On the **Marks** card, change the dropdown from *Automatic* to **Map** (fills states in).
3. Drag **Value** onto **Color** on the Marks card.
4. Right-click the **Value** pill → **Measure → Average**.
5. Now apply the Golden Rule filters — drag each to the **Filters** shelf:
   - **Metric** → check only **Obesity**
   - **DemographicCategory** → check only **Overall**
   - **Year** → choose one year (2022 has the most complete coverage). Right-click
     this Year filter → **Show Filter** so viewers can change it.
6. Rename the tab at the bottom to **Obesity Map** (double-click it).

### Sheet 2 → "Trend Over Time"
1. New sheet (bottom bar, the "+" icon).
2. Drag **Year** to **Columns**; drag **Value** to **Rows**.
3. Right-click **Value** → Measure → **Average**.
4. Filters: **Metric** = Obesity, **DemographicCategory** = Overall, **State** = National.
   (Right-click Metric filter → Show Filter so viewers can switch metrics.)
5. You now have a national trend line. Rename tab **Trend Over Time**.

### Sheet 3 → "By Demographic"
1. New sheet.
2. Drag **DemographicGroup** to **Rows**; **Value** to **Columns** (makes bars).
3. Right-click **Value** → Measure → Average.
4. Filters: **Metric** = Obesity, **State** = National, **Year** = 2022,
   **DemographicCategory** = **Income** (try Education or Race too).
5. Drag **Value** to **Color** for a nice gradient. Sort bars: click the sort icon
   on the toolbar. Rename tab **By Demographic**.

### Sheet 4 → "Key Numbers" (KPIs)
1. New sheet.
2. Double-click **Value** (shows one big number). Right-click → Measure → Average.
3. Filters: Metric = Obesity, DemographicCategory = Overall, State = National, Year = 2022.
4. This shows the national obesity rate as a big number. Rename tab **National Rate**.
   (Optional: duplicate this sheet, swap State filter to show a specific state.)

## PART 4 — Assemble the dashboard
1. Bottom bar → click the **New Dashboard** icon (grid-like icon next to New Sheet).
2. Set **Size** (left panel) to **Automatic**.
3. Drag your sheets from the left list onto the canvas: Map on top, Trend and
   Bar side by side below, KPI in a corner.
4. Add a title: **Dashboard → Show Title**, then rename it
   "U.S. Adult Obesity & Lifestyle, 2011–2024".
5. The filters you set to "Show Filter" appear on the dashboard — arrange them neatly.
6. Tip: click a filter → dropdown → **Apply to Worksheets → All Using This Data Source**
   so one Year/Metric filter controls the whole dashboard.

## PART 5 — Publish (get your shareable link)
1. Top menu → **File → Save to Tableau Public As…**
2. Sign in, give it a name, Save. Your browser opens your **live public dashboard**.
3. Copy that URL → paste it into your resume (the `[Tableau Public link]` spot) and
   into this README above.

---

## Interview talking points
- "I cleaned a 110,000-row CDC dataset down to a tidy 73,000-row file with Python (pandas), then built an interactive Tableau dashboard."
- "It shows adult obesity across states, over 2011–2024, and by income/education —
  surfacing health disparities (e.g., obesity is higher in lower-income groups)."
- "Users can filter by year and metric to explore physical activity and nutrition too."

## How to regenerate the clean data
```bash
conda activate bioinfo
python scripts/prepare_data.py
```
