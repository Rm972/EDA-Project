import pandas as pd
import streamlit as st
import plotly.express as px

from core import charts
from core.data import DEGREE_ORDER, GENDER_ORDER, WORK_ORDER
from core.insights import NUMERIC_COLUMNS
from core.ui import Context, empty_state, page_header, show_chart

DISPLAY_COLUMNS = ["Age", "age_group", "Gender", "Work", "Degree", "Hours", "streams", "is_addicted",
                   "Anxiety", "Life_Satisfaction", "Social_Phobia", "Anxiety_Impact",
                   "whyplay", "Playstyle", "earnings"]
CATEGORICAL = {"Gender": GENDER_ORDER, "age_group": None, "Work": WORK_ORDER, "Degree": DEGREE_ORDER,
               "Playstyle": None, "whyplay": None, "earnings": None, "Anxiety_Impact": None}
NUMERIC_LABELS = {"Hours": "Gaming hours per week", "streams": "Stream / coaching hours per week",
                  "Anxiety": "Anxiety (0–21)", "Life_Satisfaction": "Life satisfaction (5–35)",
                  "Social_Phobia": "Social phobia (0–68)", "Age": "Age"}


def render(ctx: Context) -> None:
    page_header("Explore the Data", "Inspect the cleaned dataset, its structure and the distribution of each variable.")
    df = ctx.filtered
    if df.empty:
        empty_state()
        return
    data = df[DISPLAY_COLUMNS]

    tab_preview, tab_structure, tab_stats, tab_dist, tab_clean = st.tabs(
        ["Preview", "Structure", "Statistics", "Distributions", "Cleaning steps"])

    with tab_preview:
        c1, c2 = st.columns([3, 1])
        with c1:
            cols = st.multiselect("Columns to show", DISPLAY_COLUMNS, default=DISPLAY_COLUMNS, key="explore_cols")
        with c2:
            st.metric("Rows shown", f"{len(data):,}")
        if cols:
            st.dataframe(data[cols], hide_index=True, height=420)
        else:
            st.info("Select at least one column.")
        st.download_button("Download filtered data (CSV)", data[cols or DISPLAY_COLUMNS].to_csv(index=False).encode("utf-8"),
                           file_name="gaming_mental_health_filtered.csv", mime="text/csv")

    with tab_structure:
        a, b, c = st.columns(3)
        a.metric("Rows (filtered)", f"{len(data):,}")
        b.metric("Columns", data.shape[1])
        c.metric("Missing values", int(data.isna().sum().sum()))
        info = pd.DataFrame({
            "Column": data.columns,
            "Type": [str(t) for t in data.dtypes],
            "Non-missing": data.notna().sum().values,
            "Unique values": data.nunique().values,
            "Example": [data[col].iloc[0] for col in data.columns],
        })
        st.dataframe(info.astype({"Example": str}), hide_index=True)

        st.markdown("##### Missing values in the original file")
        st.caption("Percentage of empty cells per column in the raw survey data (before cleaning). "
                   "The cleaned data has no missing values.")
        raw_missing = (ctx.raw.isna().mean() * 100).round(2)
        raw_missing = raw_missing[raw_missing > 0].sort_values(ascending=False).rename("Missing (%)")
        st.dataframe(raw_missing.reset_index().rename(columns={"index": "Column"}), hide_index=True, height=300)
        st.caption("Note: the 11.71% shown for Degree is not truly missing. Pandas reads the survey answer "
                   "'None' (no degree) as empty; the cleaning restores it.")

    with tab_stats:
        st.markdown("##### Numerical variables")
        st.dataframe(data[NUMERIC_COLUMNS].describe().T.round(2))
        st.markdown("##### Categorical variables")
        cat = data[list(CATEGORICAL)].astype(str).describe().T.rename(
            columns={"count": "Count", "unique": "Unique", "top": "Most common", "freq": "Frequency"})
        st.dataframe(cat)

    with tab_dist:
        left, right = st.columns(2, gap="large")
        with left:
            num = st.selectbox("Numerical variable", list(NUMERIC_LABELS), format_func=NUMERIC_LABELS.get,
                               key="explore_num")
            fig = px.histogram(data, x=num, marginal="box", nbins=40, title=NUMERIC_LABELS[num],
                               color_discrete_sequence=[charts.PRIMARY])
            fig.update_layout(xaxis_title=NUMERIC_LABELS[num], yaxis_title="Players (count)", bargap=0.05)
            show_chart(charts.style(fig, height=380, legend=False), "explore_hist")
            s = data[num]
            st.caption(f"Mean {s.mean():.1f} · Median {s.median():.1f} · Skewness {s.skew():.2f}. "
                       "The box on top shows the median, quartiles and outliers.")
        with right:
            cat_col = st.selectbox("Categorical variable", list(CATEGORICAL), key="explore_cat")
            show_chart(charts.category_counts(data, cat_col, f"Players by {cat_col}", CATEGORICAL[cat_col]),
                       "explore_cat_chart")
            st.caption("Bars show the number of players; the percentage is the share of the filtered players.")

    with tab_clean:
        st.markdown("Every step below is reproduced from the project notebook in the same order.")
        st.dataframe(pd.DataFrame(ctx.log), hide_index=True)
        st.markdown(
            "- **GADE** was an optional question that starts with *\"If you checked off any problems…\"*. "
            "Most people who skipped it had an anxiety score of 0, and 96% of people with 0 anxiety who did "
            "answer chose *Not difficult at all*, so skipped answers were filled with that value.\n"
            "- **Degree:** the survey's *None* option was read as missing by pandas; it was restored.\n"
            "- **Impossible values:** more than 168 hours per week (the length of a week) were removed.\n"
            "- High but possible values (e.g. 60 hours) were **kept**, because they are the heavy players this project studies."
        )
