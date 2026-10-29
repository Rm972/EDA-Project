"""Summary tables and plain-English findings, all calculated from the loaded data."""
from __future__ import annotations

import pandas as pd

from core.data import ADDICTION_ORDER, IMPACT_ORDER, SCORES

# Groups smaller than this are flagged as unreliable (same rule the notebook uses for text answers)
MIN_GROUP = 30
NUMERIC_COLUMNS = ["Hours", "streams", "Anxiety", "Life_Satisfaction", "Social_Phobia", "Age"]
COMPARE_PLAYSTYLES = ["Real friends", "Online friends", "Strangers", "Singleplayer"]
DEGREE_PHRASES = {
    "No degree": "no degree", "High school": "a high school diploma", "Bachelor": "a bachelor's degree",
    "Master": "a master's degree", "PhD": "a PhD",
}
PLAYSTYLE_PHRASES = {
    "Real friends": "play with real-life friends",
    "Online friends": "play with online friends",
    "Strangers": "play with strangers",
    "Singleplayer": "play alone",
}


def group_rates(df: pd.DataFrame, col: str, order: list[str] | None = None) -> pd.DataFrame:
    """Players, addicted players and addiction rate (%) for each group of `col`."""
    table = (df.groupby(col, observed=True)["is_addicted"]
             .agg(Players="size", Addicted="sum").reset_index())
    table["Addicted"] = table["Addicted"].astype(int)
    table["Addiction rate (%)"] = table["Addicted"] / table["Players"] * 100
    if order:
        rank = {v: i for i, v in enumerate(order)}
        table = table.sort_values(col, key=lambda s: s.map(rank).fillna(len(order)))
    return table.reset_index(drop=True)


def age_gender_rates(df: pd.DataFrame) -> pd.DataFrame:
    table = (df.groupby(["age_group", "Gender"], observed=True)["is_addicted"]
             .agg(Players="size", Addicted="sum").reset_index())
    table["Addicted"] = table["Addicted"].astype(int)
    table["Addiction rate (%)"] = table["Addicted"] / table["Players"] * 100
    return table


def score_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Count, mean, median and quartiles of each score for addicted vs not addicted."""
    rows = []
    for score, meta in SCORES.items():
        for status in ADDICTION_ORDER:
            s = df.loc[df["addiction_status"] == status, score]
            if s.empty:
                continue
            rows.append({
                "Score": meta["label"], "Group": status, "Players": len(s),
                "Mean": s.mean(), "Median": s.median(),
                "Q1": s.quantile(0.25), "Q3": s.quantile(0.75), "Std": s.std(),
            })
    return pd.DataFrame(rows)


def impact_table(df: pd.DataFrame) -> pd.DataFrame:
    """% of each addiction group giving each Anxiety_Impact answer (each group adds to 100%)."""
    table = pd.crosstab(df["Anxiety_Impact"], df["addiction_status"], normalize="columns") * 100
    return table.reindex(index=IMPACT_ORDER, columns=[c for c in ADDICTION_ORDER if c in table.columns]).fillna(0)


def correlations(df: pd.DataFrame) -> pd.DataFrame:
    return df[NUMERIC_COLUMNS].corr()


def mean_by(df: pd.DataFrame, col: str, value: str) -> pd.DataFrame:
    table = (df.groupby(col, observed=True)
             .agg(Players=(value, "size"), **{value: (value, "mean")}, Hours=("Hours", "mean"))
             .reset_index())
    return table.sort_values(value).reset_index(drop=True)


def key_findings(df: pd.DataFrame) -> dict[str, str]:
    """Findings written from the data (used with the full dataset)."""
    out: dict[str, str] = {}
    rate = df["is_addicted"].mean() * 100
    out["rate"] = f"**{rate:.1f}%** of players play 40+ hours per week (classified as addicted)."

    ag = age_gender_rates(df[df["Gender"].isin(["Male", "Female"])])
    ag = ag[ag["Players"] >= MIN_GROUP]
    if not ag.empty:
        top = ag.loc[ag["Addiction rate (%)"].idxmax()]
        by_age = group_rates(df, "age_group").set_index("age_group")["Addiction rate (%)"]
        trend = " and the rate goes down with every older age group" if by_age.is_monotonic_decreasing else ""
        out["age"] = (f"The most addicted group is **{top['Gender'].lower()}s aged {top['age_group']}** "
                      f"({top['Addiction rate (%)']:.1f}%){trend}.")

    work = group_rates(df, "Work")
    work = work[work["Players"] >= MIN_GROUP].set_index("Work")["Addiction rate (%)"]
    if len(work) >= 2:
        hi, lo = work.idxmax(), work.idxmin()
        out["work"] = (f"**{hi}** players have the highest addiction rate ({work[hi]:.1f}%), "
                       f"**{work[hi] / work[lo]:.1f}×** that of **{lo.lower()}** players ({work[lo]:.1f}%).")

    deg = group_rates(df, "Degree")
    deg = deg[deg["Players"] >= MIN_GROUP].set_index("Degree")["Addiction rate (%)"]
    if len(deg) >= 2:
        out["degree"] = (f"By education, players with **{DEGREE_PHRASES.get(deg.idxmax(), deg.idxmax())}** have the highest rate "
                         f"({deg.max():.1f}%) and players with **{DEGREE_PHRASES.get(deg.idxmin(), deg.idxmin())}** the lowest ({deg.min():.1f}%).")

    med = df.groupby("addiction_status")[list(SCORES)].median()
    if set(ADDICTION_ORDER) <= set(med.index):
        a, n = med.loc["Addicted"], med.loc["Not addicted"]
        out["mental"] = (
            "Addicted players have higher anxiety (median "
            f"{a['Anxiety']:.0f} vs {n['Anxiety']:.0f}), lower life satisfaction "
            f"({a['Life_Satisfaction']:.0f} vs {n['Life_Satisfaction']:.0f}) and higher social phobia "
            f"({a['Social_Phobia']:.0f} vs {n['Social_Phobia']:.0f})."
        )

    corr = correlations(df)["Hours"][list(SCORES)]
    strongest = corr.abs().max()
    out["corr"] = (f"Gaming hours are only **weakly** related to mental health "
                   f"(|r| ≤ {strongest:.2f} for all three scores).")

    why = mean_by(df, "whyplay", "Anxiety")
    why = why[why["Players"] >= MIN_GROUP]
    if len(why) >= 2:
        low, high = why.iloc[0], why.iloc[-1]
        fewer = (f", even though they play fewer hours than average ({high['Hours']:.1f} vs "
                 f"{df['Hours'].mean():.1f})") if high["Hours"] < df["Hours"].mean() else ""
        out["why"] = (f"Players whose main reason is **{low['whyplay'].lower()}** have the lowest anxiety "
                      f"({low['Anxiety']:.1f}); players whose main reason is **{high['whyplay'].lower()}** "
                      f"have the highest ({high['Anxiety']:.1f}){fewer}.")

    style = mean_by(df, "Playstyle", "Life_Satisfaction").set_index("Playstyle")
    style = style[(style["Players"] >= MIN_GROUP) & style.index.isin(COMPARE_PLAYSTYLES)]
    if len(style) >= 2:
        best, worst = style["Life_Satisfaction"].idxmax(), style["Life_Satisfaction"].idxmin()
        out["style"] = (f"Players who **{PLAYSTYLE_PHRASES[best]}** report the highest life satisfaction "
                        f"({style.loc[best, 'Life_Satisfaction']:.1f}) and players who **{PLAYSTYLE_PHRASES[worst]}** "
                        f"the lowest ({style.loc[worst, 'Life_Satisfaction']:.1f}).")
    return out
