"""Small layout helpers so every page looks the same."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from core.charts import PLOTLY_CONFIG

CSS = """
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1250px;}
h1 {font-weight: 700; letter-spacing: -0.02em;}
h2, h3 {font-weight: 650; letter-spacing: -0.01em;}
[data-testid="stMetricValue"] {font-size: 1.7rem; font-weight: 650;}
[data-testid="stMetricLabel"] p {font-size: 0.85rem; color: #475569;}
[data-testid="stCaptionContainer"] {color: #64748B;}
.page-subtitle {color: #475569; font-size: 1.05rem; margin-top: -0.6rem; margin-bottom: 1.2rem;}
.finding {border-left: 4px solid #4F46E5; background: #F8FAFF; padding: 0.7rem 1rem;
          border-radius: 0 8px 8px 0; margin-bottom: 0.6rem;}
</style>
"""


@dataclass
class Context:
    """Everything a page needs. `filtered` has all sidebar filters applied."""
    raw: pd.DataFrame
    full: pd.DataFrame
    filtered: pd.DataFrame
    log: list[dict]
    selections: dict[str, list[str]]


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)


def kpi_row(items: list[tuple[str, str, str | None]]) -> None:
    """items: (label, value, help text)."""
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        with col:
            with st.container(border=True):
                st.metric(label, value, help=help_text)


def show_chart(fig, key: str) -> None:
    st.plotly_chart(fig, config=PLOTLY_CONFIG, key=key)


def finding(text: str) -> None:
    st.markdown(f'<div class="finding">{_md_bold_to_html(text)}</div>', unsafe_allow_html=True)


def empty_state(message: str = "No players match the current filters.") -> None:
    st.info(f"{message} Use **Reset filters** in the sidebar or select more options.")


def _md_bold_to_html(text: str) -> str:
    parts = text.split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))
