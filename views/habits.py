import streamlit as st

from core import charts
from core.data import ADDICTION_THRESHOLD, SCORES
from core.filters import apply_filters, scope_note
from core.insights import COMPARE_PLAYSTYLES, MIN_GROUP, correlations, mean_by
from core.ui import Context, empty_state, page_header, show_chart

CORR_LABELS = {"Hours": "Hours", "streams": "Stream hours", "Anxiety": "Anxiety",
               "Life_Satisfaction": "Life satisfaction", "Social_Phobia": "Social phobia", "Age": "Age"}


def _strength(r: float) -> str:
    r = abs(r)
    return "very weak" if r < 0.1 else "weak" if r < 0.3 else "moderate" if r < 0.5 else "strong"


def render(ctx: Context) -> None:
    page_header("Gaming Habits and Mental Health",
                "How much, why and with whom people play, and how each relates to mental health.")
    df = ctx.filtered
    if df.empty:
        empty_state()
        return

    # ---------- Q4: hours vs mental health ----------
    st.subheader("Q4 · How strong is the link between gaming hours and mental health?")
    if len(df) < MIN_GROUP:
        st.info(f"At least {MIN_GROUP} players are needed to calculate correlations. Please widen the filters.")
    else:
        corr = correlations(df)
        left, right = st.columns([3, 2], gap="large")
        with left:
            show_chart(charts.hours_scatter(df, ADDICTION_THRESHOLD, "Gaming hours vs anxiety"), "hab_scatter")
        with right:
            r = corr.loc["Hours", list(SCORES)]
            st.markdown("**Correlation with weekly hours (r)**")
            for score, meta in SCORES.items():
                st.markdown(f"- {meta['label']}: **{r[score]:.2f}** ({_strength(r[score])})")
            st.markdown(
                "The points are spread widely with no clear line. Most players play 10–30 hours with little "
                "difference in anxiety; differences mainly appear among the heaviest players (40+ hours)."
            )
            st.caption("r ranges from −1 to 1; values near 0 mean no linear relationship.")

        show_chart(charts.correlation_heatmap(corr.rename(index=CORR_LABELS, columns=CORR_LABELS),
                                              "Correlation between numerical variables"), "hab_heatmap")
        mental = corr.loc[list(SCORES), list(SCORES)].abs()
        mental = mental.where(~mental.eq(1.0)).stack()
        pair = mental.idxmax()
        st.caption(
            f"{scope_note(ctx.full, ctx.selections)} The strongest relationship is between "
            f"**{SCORES[pair[0]]['label']}** and **{SCORES[pair[1]]['label']}** "
            f"(r = {corr.loc[pair[0], pair[1]]:.2f}): the mental health scores are more closely related to each other "
            "than to gaming hours. Correlation does not mean causation."
        )

    # ---------- Q5: reason for playing ----------
    st.subheader("Q5 · Reason for playing and anxiety")
    why_data = apply_filters(ctx.full, ctx.selections, exclude=("whyplay",))
    if why_data.empty:
        empty_state()
    else:
        why = mean_by(why_data, "whyplay", "Anxiety").iloc[::-1]
        show_chart(charts.mean_bars(why, "whyplay", "Anxiety", "Average anxiety by main reason for playing",
                                    "Average anxiety (0–21, lower is better)", MIN_GROUP, extra_hover="Hours"),
                   "hab_why")
        reliable = why[why["Players"] >= MIN_GROUP]
        if len(reliable) >= 2:
            low = reliable.loc[reliable["Anxiety"].idxmin()]
            high = reliable.loc[reliable["Anxiety"].idxmax()]
            st.markdown(
                f"Players whose main reason is **{low['whyplay'].lower()}** have the lowest average anxiety "
                f"({low['Anxiety']:.1f}); **{high['whyplay'].lower()}** has the highest ({high['Anxiety']:.1f}) "
                f"with {high['Hours']:.1f} hours/week on average. Hover over a bar to see average hours."
            )
        st.caption(scope_note(ctx.full, ctx.selections, exclude=("whyplay",)) +
                   f" Light grey bars have fewer than {MIN_GROUP} players.")

    # ---------- Q6: playstyle ----------
    st.subheader("Q6 · Playing with friends vs playing alone")
    style_data = apply_filters(ctx.full, ctx.selections, exclude=("Playstyle",))
    if style_data.empty:
        empty_state()
    else:
        style = mean_by(style_data, "Playstyle", "Life_Satisfaction")
        show_chart(charts.mean_bars(style.iloc[::-1], "Playstyle", "Life_Satisfaction",
                                    "Average life satisfaction by playstyle",
                                    "Average life satisfaction (5–35, higher is better)", MIN_GROUP),
                   "hab_style")
        main = style[style["Playstyle"].isin(COMPARE_PLAYSTYLES) & (style["Players"] >= MIN_GROUP)]
        if len(main) >= 2:
            best = main.loc[main["Life_Satisfaction"].idxmax()]
            worst = main.loc[main["Life_Satisfaction"].idxmin()]
            st.markdown(
                f"Comparing the four main playstyles, **{best['Playstyle']}** has the highest average life satisfaction "
                f"({best['Life_Satisfaction']:.1f}) and **{worst['Playstyle']}** the lowest ({worst['Life_Satisfaction']:.1f})."
            )
        st.caption(scope_note(ctx.full, ctx.selections, exclude=("Playstyle",)) +
                   " *Offline (same room)* is a very small group, and *Other* combines many free-text answers, "
                   "so neither is used in the main comparison.")

        full_table = (style_data.groupby("Playstyle")
                      .agg(Players=("Anxiety", "size"), Anxiety=("Anxiety", "mean"),
                           Life_Satisfaction=("Life_Satisfaction", "mean"), Social_Phobia=("Social_Phobia", "mean"))
                      .sort_values("Life_Satisfaction", ascending=False).round(1))
        with st.expander("All three scores by playstyle"):
            st.dataframe(full_table)
