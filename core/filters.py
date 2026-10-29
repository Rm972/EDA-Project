"""Sidebar filters shared by every page."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core.data import AGE_LABELS, DEGREE_ORDER, GENDER_ORDER, WORK_ORDER

# (column, label shown in the sidebar)
FILTERS = [
    ("age_group", "Age group"),
    ("Gender", "Gender"),
    ("Work", "Work status"),
    ("Degree", "Education"),
    ("Playstyle", "Playstyle"),
    ("whyplay", "Reason for playing"),
]
FILTER_LABELS = dict(FILTERS)

_PREFERRED_ORDER = {
    "age_group": AGE_LABELS,
    "Gender": GENDER_ORDER,
    "Work": WORK_ORDER,
    "Degree": DEGREE_ORDER,
}


def _options(df: pd.DataFrame, col: str) -> list[str]:
    present = list(pd.unique(df[col].astype(str)))
    preferred = [v for v in _PREFERRED_ORDER.get(col, []) if v in present]
    rest = sorted(v for v in present if v not in preferred)
    return preferred + rest


def _key(col: str) -> str:
    return f"filter_{col}"


def render_sidebar_filters(df: pd.DataFrame) -> dict[str, list[str]]:
    """Draw the filters and return {column: selected values}."""
    options = {col: _options(df, col) for col, _ in FILTERS}

    # Initialise once, then let the widgets own their state (no default= to avoid conflicts)
    for col, _ in FILTERS:
        st.session_state.setdefault(_key(col), options[col])

    def reset() -> None:
        for col, _ in FILTERS:
            st.session_state[_key(col)] = options[col]

    st.sidebar.markdown("### Filters")
    selections = {}
    for col, label in FILTERS:
        selections[col] = st.sidebar.multiselect(label, options[col], key=_key(col))
    st.sidebar.button("Reset filters", on_click=reset)
    return selections


def apply_filters(df: pd.DataFrame, selections: dict[str, list[str]], exclude: tuple[str, ...] = ()) -> pd.DataFrame:
    """Keep rows matching every selected filter, except the columns listed in `exclude`."""
    mask = pd.Series(True, index=df.index)
    for col, values in selections.items():
        if col in exclude:
            continue
        mask &= df[col].astype(str).isin(values)
    return df[mask]


def active_filters(df: pd.DataFrame, selections: dict[str, list[str]]) -> list[str]:
    """Columns where the user removed at least one option."""
    return [col for col, values in selections.items() if set(values) != set(_options(df, col))]


def scope_note(df: pd.DataFrame, selections: dict[str, list[str]], exclude: tuple[str, ...] = ()) -> str:
    """Plain-English note on which filters a chart uses."""
    active = active_filters(df, selections)
    ignored = [FILTER_LABELS[c] for c in exclude if c in active]
    if not active:
        return "Based on all players (no filters applied)."
    if ignored:
        return (f"Uses your sidebar filters except **{', '.join(ignored)}**, "
                "so every group on this chart can be compared.")
    return "Based on the players that match your sidebar filters."
