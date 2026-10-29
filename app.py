"""Gaming & Mental Health dashboard. Run with:  streamlit run app.py"""
import logging

import streamlit as st

from core.data import ADDICTION_THRESHOLD, DataLoadError, load_dataset
from core.filters import apply_filters, render_sidebar_filters
from core.ui import Context, inject_css
from views import addiction, explore, findings, habits, mental_health, overview

st.set_page_config(page_title="Gaming & Mental Health", page_icon=":material/sports_esports:", layout="wide")
inject_css()
logger = logging.getLogger(__name__)


@st.cache_data(show_spinner="Loading and cleaning the survey data...")
def get_data():
    return load_dataset()


try:
    raw, full, log = get_data()
except DataLoadError as err:
    st.error(str(err))
    st.stop()
except Exception:
    logger.exception("Unexpected error while loading data")
    st.error("The data could not be loaded. Check that data/GamingStudy_data.csv is the original file and try again.")
    st.stop()

# ---------- Sidebar ----------
st.sidebar.markdown("## Gaming & Mental Health")
st.sidebar.caption("Online Gaming Anxiety survey · Sauter & Draschkow (2017)")
selections = render_sidebar_filters(full)
filtered = apply_filters(full, selections)
st.sidebar.markdown(f"**{len(filtered):,}** of {len(full):,} players selected")
st.sidebar.caption(f"Addicted = {ADDICTION_THRESHOLD}+ gaming hours per week (project definition, not a diagnosis).")

ctx = Context(raw=raw, full=full, filtered=filtered, log=log, selections=selections)


def _safe(render):
    def page():
        try:
            render(ctx)
        except Exception:
            logger.exception("Error while drawing page")
            st.error("Something went wrong while drawing this page. Try **Reset filters** in the sidebar.")
    return page


pages = [
    st.Page(_safe(overview.render), title="Overview", icon=":material/dashboard:", url_path="overview", default=True),
    st.Page(_safe(explore.render), title="Explore the Data", icon=":material/table_chart:", url_path="explore"),
    st.Page(_safe(addiction.render), title="Gaming Addiction", icon=":material/sports_esports:", url_path="addiction"),
    st.Page(_safe(mental_health.render), title="Mental Health", icon=":material/psychology:", url_path="mental-health"),
    st.Page(_safe(habits.render), title="Habits & Mental Health", icon=":material/insights:", url_path="habits"),
    st.Page(_safe(findings.render), title="Findings & Limitations", icon=":material/fact_check:", url_path="findings"),
]
st.navigation(pages).run()
