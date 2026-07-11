"""
visualization.py — Multi-Chart Visualization Module
=====================================================
Generates multiple chart types (bar, pie, histogram, heatmap)
using Seaborn/Matplotlib with a dark theme. Saves all charts
to the charts/ directory and returns figure objects + metadata
for Streamlit rendering and AI explanation.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Dark-theme colour palette
# ---------------------------------------------------------------------------
DARK_BG = "#0f0c29"
CARD_BG = "#1a1a2e"
ACCENT_COLORS = ["#818cf8", "#a78bfa", "#c084fc", "#e879f9", "#f472b6",
                 "#fb7185", "#f97316", "#facc15", "#34d399", "#22d3ee"]
TEXT_COLOR = "#e2e8f0"


def _apply_dark_style():
    """Apply a custom dark style to matplotlib figures."""
    plt.rcParams.update({
        "figure.facecolor": DARK_BG,
        "axes.facecolor": CARD_BG,
        "axes.edgecolor": "#334155",
        "axes.labelcolor": TEXT_COLOR,
        "text.color": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "grid.color": "#1e293b",
        "grid.alpha": 0.4,
        "font.family": "sans-serif",
        "font.size": 11,
    })


def _ensure_dir(path):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------------------------
# Chart generators
# ---------------------------------------------------------------------------

def generate_bar_chart(df, save_dir="charts"):
    """
    Creates a bar chart of the top categories aggregated by the most
    prominent numerical column.

    Returns:
        tuple: (matplotlib Figure, metadata dict) or (None, None) if not applicable.
    """
    _apply_dark_style()
    _ensure_dir(save_dir)

    num_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=["object", "category"]).columns

    if len(cat_cols) == 0 or len(num_cols) == 0:
        return None, None

    # Pick the categorical column with lowest cardinality (more meaningful groups)
    cat_col = min(cat_cols, key=lambda c: df[c].nunique())
    # Pick the numerical column with the widest range (usually most interesting)
    num_col = max(num_cols, key=lambda c: df[c].max() - df[c].min())

    top_n = df.groupby(cat_col)[num_col].sum().nlargest(10).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        top_n[cat_col].astype(str),
        top_n[num_col],
        color=ACCENT_COLORS[: len(top_n)],
        edgecolor="none",
        width=0.65,
    )
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:,.0f}",
            ha="center", va="bottom",
            fontsize=9, color=TEXT_COLOR, fontweight="bold",
        )

    ax.set_title(f"Top {cat_col} by Total {num_col}", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel(cat_col, fontsize=12)
    ax.set_ylabel(f"Total {num_col}", fontsize=12)
    ax.tick_params(axis="x", rotation=40)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()

    save_path = os.path.join(save_dir, "bar_chart.png")
    fig.savefig(save_path, dpi=150, bbox_inches="tight")

    metadata = {
        "type": "bar_chart",
        "title": f"Top {cat_col} by Total {num_col}",
        "x_column": cat_col,
        "y_column": num_col,
        "data": top_n.to_dict(orient="records"),
    }
    return fig, metadata


def generate_pie_chart(df, save_dir="charts"):
    """
    Creates a pie chart showing the distribution of the first
    categorical column.

    Returns:
        tuple: (matplotlib Figure, metadata dict) or (None, None).
    """
    _apply_dark_style()
    _ensure_dir(save_dir)

    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(cat_cols) == 0:
        return None, None

    cat_col = min(cat_cols, key=lambda c: df[c].nunique())
    counts = df[cat_col].value_counts().head(8)

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=ACCENT_COLORS[: len(counts)],
        startangle=140,
        pctdistance=0.8,
        wedgeprops=dict(linewidth=2, edgecolor=DARK_BG),
    )
    for t in texts:
        t.set_color(TEXT_COLOR)
        t.set_fontsize(10)
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
        t.set_fontsize(9)

    ax.set_title(f"Distribution of {cat_col}", fontsize=16, fontweight="bold", pad=20)
    plt.tight_layout()

    save_path = os.path.join(save_dir, "pie_chart.png")
    fig.savefig(save_path, dpi=150, bbox_inches="tight")

    metadata = {
        "type": "pie_chart",
        "title": f"Distribution of {cat_col}",
        "column": cat_col,
        "data": {str(k): int(v) for k, v in counts.items()},
    }
    return fig, metadata


def generate_histogram(df, save_dir="charts"):
    """
    Creates a histogram with KDE overlay for the first numerical column.

    Returns:
        tuple: (matplotlib Figure, metadata dict) or (None, None).
    """
    _apply_dark_style()
    _ensure_dir(save_dir)

    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) == 0:
        return None, None

    # Pick the column with the most unique values for a meaningful distribution
    num_col = max(num_cols, key=lambda c: df[c].nunique())

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(
        df[num_col].dropna(), kde=True, ax=ax,
        color=ACCENT_COLORS[0], edgecolor=CARD_BG,
        line_kws={"linewidth": 2, "color": ACCENT_COLORS[4]},
    )

    # Add mean line
    mean_val = df[num_col].mean()
    ax.axvline(mean_val, color=ACCENT_COLORS[3], linestyle="--", linewidth=1.5,
               label=f"Mean: {mean_val:,.2f}")
    ax.legend(fontsize=10, facecolor=CARD_BG, edgecolor="#334155")

    ax.set_title(f"Distribution of {num_col}", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel(num_col, fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()

    save_path = os.path.join(save_dir, "histogram.png")
    fig.savefig(save_path, dpi=150, bbox_inches="tight")

    stats = df[num_col].describe()
    metadata = {
        "type": "histogram",
        "title": f"Distribution of {num_col}",
        "column": num_col,
        "summary_stats": {k: round(float(v), 4) for k, v in stats.items()},
    }
    return fig, metadata


def generate_correlation_heatmap(df, save_dir="charts"):
    """
    Creates a correlation heatmap for all numerical columns.

    Returns:
        tuple: (matplotlib Figure, metadata dict) or (None, None).
    """
    _apply_dark_style()
    _ensure_dir(save_dir)

    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) < 2:
        return None, None

    corr = df[num_cols].corr().round(3)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="cool", ax=ax,
        linewidths=0.5, linecolor=CARD_BG,
        cbar_kws={"shrink": 0.8},
        annot_kws={"fontsize": 10, "color": "white"},
    )
    ax.set_title("Correlation Heatmap", fontsize=16, fontweight="bold", pad=15)
    plt.tight_layout()

    save_path = os.path.join(save_dir, "correlation_heatmap.png")
    fig.savefig(save_path, dpi=150, bbox_inches="tight")

    # Find strongest correlations (excluding self-correlations)
    strong = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            val = corr.iloc[i, j]
            if abs(val) > 0.5:
                strong.append({
                    "col_a": corr.columns[i],
                    "col_b": corr.columns[j],
                    "correlation": float(val),
                })

    metadata = {
        "type": "correlation_heatmap",
        "title": "Correlation Heatmap",
        "columns": num_cols.tolist(),
        "strong_correlations": strong,
    }
    return fig, metadata


# ---------------------------------------------------------------------------
# Master function — returns all available charts
# ---------------------------------------------------------------------------

def generate_all_charts(df, save_dir="charts"):
    """
    Generates all applicable chart types and returns them in a dict.

    Returns:
        dict: {chart_name: {"fig": Figure, "metadata": dict}} for each
              successfully generated chart. Keys are:
              'bar_chart', 'pie_chart', 'histogram', 'correlation_heatmap'.
    """
    charts = {}
    generators = [
        ("bar_chart", generate_bar_chart),
        ("pie_chart", generate_pie_chart),
        ("histogram", generate_histogram),
        ("correlation_heatmap", generate_correlation_heatmap),
    ]
    for name, func in generators:
        try:
            fig, meta = func(df, save_dir)
            if fig is not None:
                charts[name] = {"fig": fig, "metadata": meta}
        except Exception:
            # Skip charts that fail silently
            continue
    return charts
