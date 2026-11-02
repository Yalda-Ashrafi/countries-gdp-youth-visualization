"""Create a scatter plot of youth share against total GDP.

Run from this directory with: python analysis.py
Requires matplotlib (install with: python -m pip install matplotlib).
"""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


DATA_FILE = Path(__file__).with_name("countries_population_gdp_youth.csv")
OUTPUT_FILE = Path(__file__).with_name("Correlation_GDP_Youth.png")

# The source includes World Bank regional, income, and development-group totals.
AGGREGATES = {
    "Africa Eastern and Southern",
    "Africa Western and Central",
    "Arab World",
    "Caribbean small states",
    "Central Europe and the Baltics",
    "East Asia & Pacific",
    "East Asia & Pacific (excluding high income)",
    "East Asia & Pacific (IDA & IBRD countries)",
    "Early-demographic dividend",
    "Europe & Central Asia",
    "Europe & Central Asia (excluding high income)",
    "Europe & Central Asia (IDA & IBRD countries)",
    "Euro area",
    "European Union",
    "Fragile and conflict affected situations",
    "Heavily indebted poor countries (HIPC)",
    "High income",
    "IBRD only",
    "IDA & IBRD total",
    "IDA blend",
    "IDA only",
    "IDA total",
    "Latin America & Caribbean",
    "Latin America & Caribbean (excluding high income)",
    "Latin America & the Caribbean (IDA & IBRD countries)",
    "Late-demographic dividend",
    "Least developed countries: UN classification",
    "Low & middle income",
    "Low income",
    "Lower middle income",
    "Middle East, North Africa, Afghanistan & Pakistan",
    "Middle East, North Africa, Afghanistan & Pakistan (excluding high income)",
    "Middle East, North Africa, Afghanistan & Pakistan (IDA & IBRD)",
    "Middle income",
    "North America",
    "OECD members",
    "Other small states",
    "Pacific island small states",
    "Post-demographic dividend",
    "Pre-demographic dividend",
    "Small states",
    "South Asia",
    "South Asia (IDA & IBRD)",
    "Sub-Saharan Africa",
    "Sub-Saharan Africa (excluding high income)",
    "Sub-Saharan Africa (IDA & IBRD countries)",
    "Upper middle income",
    "World",
    "Not classified",
}


def load_data() -> tuple[list[dict[str, float | str]], dict[str, int]]:
    """Validate the CSV and return country/economy observations with usable values."""
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"CSV file not found: {DATA_FILE}")

    with DATA_FILE.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        expected_columns = {"Country Name", "Population", "GDP", "Youth_pct"}
        if reader.fieldnames is None or not expected_columns.issubset(reader.fieldnames):
            raise ValueError(
                f"Expected CSV columns {sorted(expected_columns)}; "
                f"found {reader.fieldnames}"
            )
        rows = list(reader)

    names = [row["Country Name"].strip() for row in rows]
    if any(not name for name in names):
        raise ValueError("CSV contains a row with an empty country/economy name.")
    if len(set(names)) != len(names):
        raise ValueError("CSV contains duplicate country/economy names.")

    missing_gdp = 0
    missing_youth = 0
    missing_population = 0
    aggregate_rows = 0
    observations: list[dict[str, float | str]] = []

    for row in rows:
        name = row["Country Name"].strip()
        gdp_text = row["GDP"].strip()
        youth_text = row["Youth_pct"].strip()
        population_text = row["Population"].strip()
        if not gdp_text:
            missing_gdp += 1
        if not youth_text:
            missing_youth += 1
        if not population_text:
            missing_population += 1
        if name in AGGREGATES:
            aggregate_rows += 1
            continue

        if not gdp_text or not youth_text:
            continue

        try:
            gdp = float(gdp_text)
            youth = float(youth_text)
            population = float(population_text) if population_text else math.nan
        except ValueError as exc:
            raise ValueError(f"Invalid numeric data for {name!r}.") from exc

        if not math.isfinite(gdp) or gdp <= 0:
            raise ValueError(f"GDP must be a positive finite number for {name!r}.")
        if not math.isfinite(youth) or not 0 <= youth <= 100:
            raise ValueError(f"Youth_pct must be between 0 and 100 for {name!r}.")
        if not math.isnan(population) and (
            not math.isfinite(population) or population < 0
        ):
            raise ValueError(f"Population must be a non-negative number for {name!r}.")

        observations.append(
            {"name": name, "gdp": gdp, "youth": youth, "population": population}
        )

    if len(observations) < 2:
        raise ValueError("At least two valid country/economy observations are needed.")

    quality = {
        "rows": len(rows),
        "missing_gdp": missing_gdp,
        "missing_youth": missing_youth,
        "missing_population": missing_population,
        "aggregate_rows": aggregate_rows,
        "plotted": len(observations),
    }
    return observations, quality


def make_chart(
    observations: list[dict[str, float | str]], quality: dict[str, int]
) -> None:
    """Save a readable scatter plot with a fitted trend on the log-GDP scale."""
    log_gdp = [math.log10(float(point["gdp"])) for point in observations]
    youth = [float(point["youth"]) for point in observations]
    mean_x = statistics.mean(log_gdp)
    mean_y = statistics.mean(youth)
    variance_x = sum((x - mean_x) ** 2 for x in log_gdp)
    if variance_x == 0:
        raise ValueError("GDP values do not vary; a correlation cannot be calculated.")

    covariance = sum(
        (x - mean_x) * (y - mean_y) for x, y in zip(log_gdp, youth)
    )
    variance_y = sum((y - mean_y) ** 2 for y in youth)
    correlation = (
        covariance / math.sqrt(variance_x * variance_y) if variance_y else math.nan
    )
    slope = covariance / variance_x
    intercept = mean_y - slope * mean_x

    figure, axis = plt.subplots(figsize=(12, 8), facecolor="#f4f8f7")
    axis.set_facecolor("#fcfdfd")
    axis.scatter(
        [float(point["gdp"]) for point in observations],
        youth,
        s=42,
        color="#16827d",
        alpha=0.72,
        edgecolors="white",
        linewidths=0.7,
        zorder=3,
    )
    axis.set_xscale("log")
    x_min = min(float(point["gdp"]) for point in observations)
    x_max = max(float(point["gdp"]) for point in observations)
    trend_x = [x_min, x_max]
    axis.plot(
        trend_x,
        [intercept + slope * math.log10(value) for value in trend_x],
        color="#d58b47",
        linestyle=(0, (5, 4)),
        linewidth=2.5,
        label="Linear trend (log GDP)",
        zorder=2,
    )

    labels = {
        "Central African Republic": (8, 12),
        "Niger": (8, -15),
        "India": (8, 8),
        "United States": (-8, 8),
    }
    for point in observations:
        name = str(point["name"])
        if name in labels:
            axis.annotate(
                name,
                (float(point["gdp"]), float(point["youth"])),
                xytext=labels[name],
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                color="#27474d",
                arrowprops={"arrowstyle": "-", "color": "#789095", "lw": 0.8},
            )

    def format_gdp(value: float, _position: int) -> str:
        if value >= 1e12:
            return f"${value / 1e12:g}T"
        if value >= 1e9:
            return f"${value / 1e9:g}B"
        if value >= 1e6:
            return f"${value / 1e6:g}M"
        return f"${value:,.0f}"

    axis.xaxis.set_major_formatter(FuncFormatter(format_gdp))
    axis.set_xlabel(
        "Total GDP (USD, logarithmic scale)", labelpad=12, fontweight="normal"
    )
    axis.set_ylabel("Population aged 0–14 (%)", labelpad=10, fontweight="normal")
    axis.set_ylim(8, 52)
    axis.grid(color="#dce6e4", linewidth=0.8, alpha=0.9)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#c4d2d0")
    axis.tick_params(colors="#536d72")
    axis.legend(frameon=False, loc="upper right")

    figure.suptitle(
        "Youth share tends to be lower in higher-GDP economies",
        x=0.09,
        y=0.97,
        ha="left",
        fontsize=19,
        fontweight="bold",
        color="#17333a",
    )
    figure.text(
        0.09,
        0.925,
        f"{quality['plotted']} countries/economies  ·  "
        f"Pearson r = {correlation:+.2f}  ·  moderate negative association",
        ha="left",
        fontsize=11,
        color="#557078",
    )
    figure.text(
        0.09,
        0.025,
        "Source: countries_population_gdp_youth.csv. Aggregate groups and rows "
        "missing GDP or youth share excluded.\n"
        "Total GDP is influenced by population size; this descriptive correlation "
        "is not causal and is not GDP per capita.",
        ha="left",
        fontsize=8.5,
        color="#657b80",
    )
    figure.tight_layout(rect=(0.07, 0.09, 0.98, 0.89))
    figure.savefig(OUTPUT_FILE, dpi=220, facecolor=figure.get_facecolor())
    plt.close(figure)
    print(f"Saved chart: {OUTPUT_FILE}")
    print(
        f"Rows: {quality['rows']}; aggregate/classification entries excluded: "
        f"{quality['aggregate_rows']}; missing GDP: {quality['missing_gdp']}; "
        f"missing youth share: {quality['missing_youth']}; "
        f"missing population: {quality['missing_population']}; "
        f"observations plotted: {quality['plotted']}."
    )
    print(f"Pearson correlation (youth share vs log10 total GDP): {correlation:.3f}")


if __name__ == "__main__":
    data, data_quality = load_data()
    make_chart(data, data_quality)
