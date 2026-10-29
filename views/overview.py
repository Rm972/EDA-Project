import streamlit as st

from core import charts
from core.data import ADDICTION_THRESHOLD
from core.insights import key_findings
from core.ui import Context, empty_state, finding, kpi_row, page_header, show_chart


def render(ctx: Context) -> None:
    page_header(
        "Gaming & Mental Health",
        "Are gamers sad and isolated? An exploratory analysis of how gaming habits relate to "
        "anxiety, life satisfaction and social phobia in a survey of over 13,000 players.",
    )

    df = ctx.filtered
    if df.empty:
        empty_state()
        return

    total = len(ctx.full)
    scope = "all players" if len(df) == total else f"{len(df):,} of {total:,} players (filtered)"
    st.caption(f"The numbers below use **{scope}**.")
    if len(df) < 30:
        st.warning("Fewer than 30 players match these filters, so the numbers below are not reliable.")

    kpi_row([
        ("Participants", f"{len(df):,}", f"Players in the cleaned dataset that match the filters (out of {total:,})."),
        ("Average weekly hours", f"{df['Hours'].mean():.1f}", f"Median: {df['Hours'].median():.0f} hours."),
        ("Classified as addicted", f"{df['is_addicted'].mean() * 100:.1f}%",
         f"Share of players who play {ADDICTION_THRESHOLD}+ hours per week (project definition)."),
        ("Average anxiety", f"{df['Anxiety'].mean():.1f} / 21", "GAD-7 score, higher = more anxiety."),
        ("Average life satisfaction", f"{df['Life_Satisfaction'].mean():.1f} / 35",
         "SWL score (5–35), higher = more satisfied."),
    ])

    st.write("")
    left, right = st.columns([3, 2], gap="large")
    with left:
        fig = charts.histogram(df, "Hours", "Weekly gaming hours", "Hours per week", nbins=40,
                               line_at=ADDICTION_THRESHOLD, line_label=f"{ADDICTION_THRESHOLD}h addiction line")
        show_chart(fig, "overview_hours")
        st.caption(
            f"Mean {df['Hours'].mean():.1f} h, median {df['Hours'].median():.0f} h, skewness "
            f"{df['Hours'].skew():.2f}: the distribution is right-skewed. Most players play a moderate "
            "amount and a smaller group plays much more. Players right of the dashed line are classified as addicted."
        )
    with right:
        st.subheader("Key findings")
        st.caption("Calculated from the full cleaned dataset, not the filters.")
        findings = key_findings(ctx.full)
        for k in ["rate", "age", "work", "mental", "corr", "why"]:
            if k in findings:
                finding(findings[k])

    with st.expander("About this project and the addiction definition"):
        st.markdown(
            "- **Data:** Online Gaming Anxiety Data (Kaggle), originally collected by Sauter & Draschkow (2017).\n"
            f"- **Addicted** means playing **{ADDICTION_THRESHOLD}+ hours per week** (the length of a full-time job). "
            "This is an analytical definition for this project, **not a medical diagnosis**.\n"
            "- **Scores:** Anxiety (GAD-7, 0–21), Life satisfaction (SWL, 5–35), Social phobia (SPIN, 0–68).\n"
            "- Results show **associations**, not causes."
        )
