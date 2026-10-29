import streamlit as st

from core import charts
from core.data import ADDICTION_ORDER, SCORES
from core.filters import scope_note
from core.insights import impact_table, score_summary
from core.ui import Context, empty_state, page_header, show_chart


def render(ctx: Context) -> None:
    page_header(
        "Mental Health Analysis",
        "Q3 · Do players classified as addicted have higher anxiety, lower life satisfaction and higher social phobia?",
    )
    df = ctx.filtered
    if df.empty:
        empty_state()
        return
    groups = df["addiction_status"].value_counts()
    if any(groups.get(g, 0) == 0 for g in ADDICTION_ORDER):
        st.info("The current filters contain only one group (addicted or not addicted), so they cannot be compared. "
                "Please widen the filters.")
        return
    small = [g for g in ADDICTION_ORDER if groups.get(g, 0) < 30]
    if small:
        st.warning(f"Fewer than 30 players in: {', '.join(small)}. Results for this selection are not reliable.")

    st.caption(f"{scope_note(ctx.full, ctx.selections)} Addicted: {groups['Addicted']:,} players · "
               f"Not addicted: {groups['Not addicted']:,} players.")

    cols = st.columns(3)
    for col, (score, meta) in zip(cols, SCORES.items()):
        with col:
            title = f"{meta['label']} · {meta['better']} is better"
            show_chart(charts.score_box(df, score, title, ADDICTION_ORDER), f"mh_box_{score}")

    grouped = df.groupby("addiction_status")[list(SCORES)]
    med, q1, q3 = grouped.median(), grouped.quantile(0.25), grouped.quantile(0.75)
    a, n = med.loc["Addicted"], med.loc["Not addicted"]
    boxes_overlap = all(q1.loc["Addicted", s] <= q3.loc["Not addicted", s] and
                        q1.loc["Not addicted", s] <= q3.loc["Addicted", s] for s in SCORES)
    overlap_text = ("The boxes (middle 50% of each group) overlap, so the difference is moderate: many addicted "
                    "players have good scores and many non-addicted players do not."
                    if boxes_overlap else "For at least one score the middle 50% of the two groups do not overlap.")
    st.markdown(
        f"Median scores, addicted vs not addicted: anxiety **{a['Anxiety']:.0f} vs {n['Anxiety']:.0f}**, "
        f"life satisfaction **{a['Life_Satisfaction']:.0f} vs {n['Life_Satisfaction']:.0f}**, "
        f"social phobia **{a['Social_Phobia']:.0f} vs {n['Social_Phobia']:.0f}**. {overlap_text}"
    )

    st.subheader("Score distributions")
    st.caption("Each group is scaled to 100%, so the shapes can be compared even though there are far more "
               "non-addicted players.")
    tabs = st.tabs([meta["label"] for meta in SCORES.values()])
    for tab, (score, meta) in zip(tabs, SCORES.items()):
        with tab:
            show_chart(charts.score_distribution(df, score, f"{meta['label']} ({meta['range']})", ADDICTION_ORDER),
                       f"mh_dist_{score}")

    st.subheader("Summary statistics")
    summary = score_summary(df).round(2)
    st.dataframe(summary, hide_index=True)
    means = df.groupby("addiction_status")[list(SCORES)].mean()
    same_direction = all((means.loc["Addicted", s] - means.loc["Not addicted", s]) *
                         (med.loc["Addicted", s] - med.loc["Not addicted", s]) >= 0 for s in SCORES)
    if same_direction:
        st.caption("Mean and median point in the same direction for every score, "
                   "so the differences are not driven by a few extreme values.")
    else:
        st.caption("Mean and median disagree for at least one score in this selection; interpret it with care.")

    st.subheader("Does anxiety affect daily life?")
    st.caption('Survey question (optional): *"If you checked off any problems, how difficult have these made it for you '
               'to do your work, take care of things at home, or get along with other people?"*')
    impact = impact_table(df)
    show_chart(charts.impact_bars(impact, "How much anxiety problems affect daily life"), "mh_impact")
    st.caption(
        f"**{impact.loc['Extremely difficult', 'Addicted']:.1f}%** of addicted players answered *extremely difficult*, "
        f"compared with **{impact.loc['Extremely difficult', 'Not addicted']:.1f}%** of non-addicted players. "
        "Each group adds up to 100%."
    )

    st.warning("**Association, not causation.** These results do not show that gaming causes mental health problems. "
               "It is equally possible that people who are anxious or unhappy play more, for example to escape stress.")
