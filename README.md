# GDP and Youth Share Visualization

This project explores the relationship between a country's youth population
share and its total GDP, and includes redesigned examples of three supplied
visualizations.

## Project files

- `countries_population_gdp_youth.csv` — source data.
- `analysis.py` — validates the data and generates the GDP/youth scatter plot.
- `Correlation_GDP_Youth.png` — generated scatter plot.
- `Corrected_Election_Graphic.png` — corrected scale using the supplied 46%
  and 47% values.
- `Corrected_Cost_Trend_Mockup.png` — illustrative line-chart redesign.
- `Corrected_Ancestry_Mockup.png` — illustrative normalized bar-chart redesign.

The cost and ancestry charts are mockups with invented example values, not
results from the original visualizations. Their source data was not provided.

## Run the analysis

Requires Python 3.10 or later.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python analysis.py
```

The script writes `Correlation_GDP_Youth.png` next to itself. It checks the
CSV columns, duplicate names, numeric values, and valid ranges. It excludes
regional/income aggregate entries and rows missing GDP or youth share; the
provided data yields 200 plotted observations.

The chart uses a logarithmic x-axis for total GDP and reports a Pearson
correlation of approximately -0.35 between youth share and log10(total GDP).
This is a descriptive association, not evidence of causation. Total GDP is
affected by population size and is not GDP per capita.
