import streamlit as st

from core import charts
from core.data import ADDICTION_THRESHOLD, AGE_LABELS, DEGREE_ORDER, GENDER_ORDER, WORK_ORDER
from core.filters import apply_filters, scope_note
from core.insights import MIN_GROUP, age_gender_rates, group_rates
from core.ui import Context, empty_state, page_header, show_chart


def _small_groups_note(table, col) -> None:
    small = table.loc[table["Players"] < MIN_GROUP, col].astype(str).tolist()
    if small:
        st.caption(f"Light grey bars have fewer than {MIN_GROUP} players ({', '.join(small)}), so they are less reliable.")


def _rate_section(ctx: Context, col: str, order: list[str], title: str, key: str):
    data = apply_filters(ctx.full, ctx.selections, exclude=(col,))
    if data.empty:
        empty_state()
        return None
    table = group_rates(data, col, order)
    # Reverse so the first category in the order appears at the top of a horizontal chart
    show_chart(charts.rate_bars(table.iloc[::-1], col, title, MIN_GROUP), key)
    st.caption(scope_note(ctx.full, ctx.selections, exclude=(col,)))
    _small_groups_note(table, col)
    return table


def render(ctx: Context) -> None:
    page_header(
        "Gaming Addiction Analysis",
        f"Who plays {ADDICTION_THRESHOLD}+ hours per week? Each bar shows the percentage of addicted players "
        "within that group, so groups of different sizes can be compared fairly.",
    )
    if ctx.filtered.empty:
        empty_state()
        return

    st.info(
        f"**Definition:** a player is classified as *addicted* if they play **{ADDICTION_THRESHOLD} hours or more per week**. "
        "This is the project's analytical definition, not a medical diagnosis. "
        "Bars show **percentages within each group**; the number of players (n) is shown next to each bar."
    )

    st.subheader("Q1 · Age and gender")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        _rate_section(ctx, "age_group", AGE_LABELS, "Addiction rate by age group", "add_age")
    with c2:
        _rate_section(ctx, "Gender", GENDER_ORDER, "Addiction rate by gender", "add_gender")

    data = apply_filters(ctx.full, ctx.selections, exclude=("age_group", "Gender"))
    data = data[data["Gender"].isin(["Male", "Female"])]
    if not data.empty:
        table = age_gender_rates(data)
        fig = charts.age_gender_bars(table, "Addiction rate by age group and gender")
        fig.update_xaxes(categoryorder="array", categoryarray=AGE_LABELS)
        show_chart(fig, "add_age_gender")
        small = table[table["Players"] < MIN_GROUP]
        notes = [scope_note(ctx.full, ctx.selections, exclude=("age_group", "Gender")),
                 "The *Other* gender group is not shown here because it is too small to split by age."]
        if not small.empty:
            notes.append("Small groups (< 30 players): " + ", ".join(
                f"{g} {a} (n={n})" for a, g, n in zip(small["age_group"], small["Gender"], small["Players"])) + ".")
        st.caption(" ".join(notes))

    st.subheader("Q2 · Work status and education")
    c3, c4 = st.columns(2, gap="large")
    with c3:
        work = _rate_section(ctx, "Work", WORK_ORDER, "Addiction rate by work status", "add_work")
    with c4:
        degree = _rate_section(ctx, "Degree", DEGREE_ORDER, "Addiction rate by education", "add_degree")
    st.caption("These are associations. For example, unemployed players may have more free time, "
               "or heavy gaming may make it harder to keep a job; the survey cannot tell which.")

    with st.expander("Show counts and percentages"):
        st.caption("Players = number of people in the group (count). Addicted = how many of them play 40+ hours (count). "
                   "Addiction rate = Addicted ÷ Players × 100.")
        for name, table in [("Work status", work), ("Education", degree)]:
            if table is not None:
                st.markdown(f"**{name}**")
                st.dataframe(table.round({"Addiction rate (%)": 1}), hide_index=True)
