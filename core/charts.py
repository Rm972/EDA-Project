"""Plotly chart builders with one consistent style."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Palette: calm indigo/slate base, one warm accent for "Addicted"
PRIMARY = "#4F46E5"
ACCENT = "#F05D5E"
NEUTRAL = "#94A3B8"
SMALL_SAMPLE = "#CBD5E1"
TEXT = "#0F172A"
GRID = "#E2E8F0"
ADDICTION_COLORS = {"Not addicted": NEUTRAL, "Addicted": ACCENT}
GENDER_COLORS = {"Male": PRIMARY, "Female": "#DB6FA0", "Other": "#14B8A6"}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}


def style(fig: go.Figure, height: int = 380, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=TEXT),
        title=dict(font=dict(size=16), x=0, xanchor="left"),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=""),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, title_font=dict(size=12))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title_font=dict(size=12))
    return fig


def rate_bars(table: pd.DataFrame, category: str, title: str, min_group: int, height: int = 360) -> go.Figure:
    """Horizontal bars of addiction rate per group. Small groups are drawn in light grey."""
    colors = [ACCENT if n >= min_group else SMALL_SAMPLE for n in table["Players"]]
    fig = go.Figure(go.Bar(
        x=table["Addiction rate (%)"],
        y=table[category],
        orientation="h",
        marker_color=colors,
        text=[f"{r:.1f}%  (n={n:,})" for r, n in zip(table["Addiction rate (%)"], table["Players"])],
        textposition="outside",
        cliponaxis=False,
        customdata=table[["Players", "Addicted"]].to_numpy(),
        hovertemplate="<b>%{y}</b><br>Addiction rate: %{x:.1f}%"
                      "<br>Addicted players: %{customdata[1]:,}<br>Players in group: %{customdata[0]:,}<extra></extra>",
    ))
    upper = max(float(table["Addiction rate (%)"].max()), 1.0) * 1.35
    fig.update_layout(title=title, xaxis_title="% addicted within each group", yaxis_title="")
    fig.update_xaxes(range=[0, upper], ticksuffix="%")
    return style(fig, height=height, legend=False)


def age_gender_bars(table: pd.DataFrame, title: str) -> go.Figure:
    fig = px.bar(
        table, x="age_group", y="Addiction rate (%)", color="Gender", barmode="group",
        color_discrete_map=GENDER_COLORS, text="Addiction rate (%)",
        custom_data=["Players", "Addicted"], title=title,
    )
    fig.update_traces(
        texttemplate="%{y:.1f}%", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Addiction rate: %{y:.1f}%"
                      "<br>Addicted players: %{customdata[1]:,}<br>Players in group: %{customdata[0]:,}<extra></extra>",
    )
    fig.update_layout(xaxis_title="Age group", yaxis_title="% addicted within group")
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    return style(fig)


def score_box(df: pd.DataFrame, score: str, title: str, order: list[str]) -> go.Figure:
    fig = px.box(
        df, x="addiction_status", y=score, color="addiction_status",
        category_orders={"addiction_status": order}, color_discrete_map=ADDICTION_COLORS,
        points=False, title=title,
    )
    fig.update_layout(xaxis_title="", yaxis_title="Score")
    return style(fig, height=340, legend=False)


def score_distribution(df: pd.DataFrame, score: str, title: str, order: list[str]) -> go.Figure:
    """Overlaid histograms; each group is scaled to 100% so different group sizes compare fairly."""
    fig = px.histogram(
        df, x=score, color="addiction_status", histnorm="percent", barmode="overlay",
        category_orders={"addiction_status": order}, color_discrete_map=ADDICTION_COLORS,
        opacity=0.65, title=title,
    )
    fig.update_traces(hovertemplate="Score %{x}<br>%{y:.1f}% of group<extra></extra>")
    fig.update_layout(xaxis_title="Score", yaxis_title="% of players in group")
    fig.update_yaxes(ticksuffix="%")
    return style(fig, height=340)


def histogram(df: pd.DataFrame, col: str, title: str, x_title: str, nbins: int | None = None,
              line_at: float | None = None, line_label: str = "") -> go.Figure:
    fig = px.histogram(df, x=col, nbins=nbins, title=title, color_discrete_sequence=[PRIMARY])
    fig.update_traces(hovertemplate=f"{x_title}: %{{x}}<br>Players: %{{y:,}}<extra></extra>")
    if line_at is not None:
        fig.add_vline(x=line_at, line_dash="dash", line_color=ACCENT, line_width=2,
                      annotation_text=line_label, annotation_position="top right",
                      annotation_font_color=ACCENT)
    fig.update_layout(xaxis_title=x_title, yaxis_title="Players (count)", bargap=0.05)
    return style(fig, height=340, legend=False)


def category_counts(df: pd.DataFrame, col: str, title: str, order: list[str] | None = None) -> go.Figure:
    counts = df[col].astype(str).value_counts()
    if order:
        counts = counts.reindex([o for o in order if o in counts.index] + [i for i in counts.index if i not in order])
    pct = counts / counts.sum() * 100
    fig = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h", marker_color=PRIMARY,
        text=[f"{c:,}  ({p:.1f}%)" for c, p in zip(counts.values, pct.values)],
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Players: %{x:,}<extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title="Players (count)", yaxis_title="")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, counts.max() * 1.3])
    return style(fig, height=max(260, 60 * len(counts) + 80), legend=False)


def impact_bars(table: pd.DataFrame, title: str) -> go.Figure:
    long = table.reset_index().melt(id_vars="Anxiety_Impact", var_name="addiction_status", value_name="pct")
    fig = px.bar(
        long, x="Anxiety_Impact", y="pct", color="addiction_status", barmode="group",
        color_discrete_map=ADDICTION_COLORS, text="pct", title=title,
    )
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", cliponaxis=False,
                      hovertemplate="<b>%{x}</b><br>%{y:.1f}% of group<extra></extra>")
    fig.update_layout(xaxis_title="", yaxis_title="% of players in group")
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    return style(fig)


def correlation_heatmap(corr: pd.DataFrame, title: str) -> go.Figure:
    fig = px.imshow(
        corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
        aspect="auto", title=title,
    )
    fig.update_traces(hovertemplate="%{x} vs %{y}<br>r = %{z:.2f}<extra></extra>")
    fig.update_layout(coloraxis_colorbar=dict(title="r", thickness=12))
    fig = style(fig, height=430, legend=False)
    fig.update_xaxes(showgrid=False, linecolor="white")
    fig.update_yaxes(showgrid=False)
    return fig


def hours_scatter(df: pd.DataFrame, threshold: float, title: str) -> go.Figure:
    fig = px.scatter(
        df, x="Hours", y="Anxiety", color="addiction_status", color_discrete_map=ADDICTION_COLORS,
        opacity=0.35, render_mode="webgl", title=title,
        category_orders={"addiction_status": ["Not addicted", "Addicted"]},
    )
    fig.update_traces(marker=dict(size=5), hovertemplate="Hours: %{x}<br>Anxiety: %{y}<extra></extra>")
    fig.add_vline(x=threshold, line_dash="dash", line_color=ACCENT, line_width=1.5)
    fig.update_layout(xaxis_title="Gaming hours per week", yaxis_title="Anxiety score (0–21)")
    return style(fig, height=400)


def mean_bars(table: pd.DataFrame, category: str, value: str, title: str, x_title: str,
              min_group: int, extra_hover: str | None = None) -> go.Figure:
    """Horizontal bars of a group average, with group size. Small groups drawn in light grey."""
    colors = [PRIMARY if n >= min_group else SMALL_SAMPLE for n in table["Players"]]
    hover = f"<b>%{{y}}</b><br>{x_title}: %{{x:.1f}}<br>Players: %{{customdata[0]:,}}"
    custom_cols = ["Players"]
    if extra_hover:
        custom_cols.append(extra_hover)
        hover += "<br>Average hours/week: %{customdata[1]:.1f}"
    fig = go.Figure(go.Bar(
        x=table[value], y=table[category], orientation="h", marker_color=colors,
        text=[f"{v:.1f}  (n={n:,})" for v, n in zip(table[value], table["Players"])],
        textposition="outside", cliponaxis=False,
        customdata=table[custom_cols].to_numpy(),
        hovertemplate=hover + "<extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title="")
    fig.update_xaxes(range=[0, float(table[value].max()) * 1.3])
    return style(fig, height=max(280, 52 * len(table) + 90), legend=False)
