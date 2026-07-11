"""
analysis.py — Enhanced Data Analysis Module
============================================
Provides functions for loading CSV data, computing dataset info,
statistical summaries, data quality reports, correlation matrices,
and column role hints for AI agent context.
"""

import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def load_data(file_path):
    """
    Safely loads a dataset (CSV, Excel, JSON, Parquet) into a pandas DataFrame.
    """
    if hasattr(file_path, "name"):
        filename = file_path.name.lower()
    else:
        filename = str(file_path).lower()

    try:
        if filename.endswith(".csv"):
            encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
            for enc in encodings:
                try:
                    if hasattr(file_path, "seek"): file_path.seek(0)
                    df = pd.read_csv(file_path, encoding=enc)
                    if df.empty: return None, "The CSV file is empty."
                    return df, None
                except UnicodeDecodeError:
                    continue
            return None, "Failed to load CSV: Unknown encoding."
        elif filename.endswith((".xlsx", ".xls")):
            if hasattr(file_path, "seek"): file_path.seek(0)
            df = pd.read_excel(file_path)
            return df, None
        elif filename.endswith(".json"):
            if hasattr(file_path, "seek"): file_path.seek(0)
            df = pd.read_json(file_path)
            return df, None
        elif filename.endswith(".parquet"):
            if hasattr(file_path, "seek"): file_path.seek(0)
            df = pd.read_parquet(file_path)
            return df, None
        else:
            return None, "Unsupported file format. Please upload CSV, Excel, JSON, or Parquet."
    except Exception as e:
        return None, f"Failed to load dataset: {str(e)}"


@st.cache_data
def get_dataset_info(df):
    """
    Returns a dictionary with basic dataset metadata.

    Keys: total_rows, total_columns, columns, missing_values, data_types.
    """
    info = {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "columns": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
    }
    return info


@st.cache_data
def get_statistical_summary(df):
    """
    Generates a statistical summary for numerical columns (mean, max, min, count)
    and frequency distribution for categorical columns.

    Returns:
        dict with keys 'numerical' and 'categorical'.
    """
    summary = {}

    # --- Numerical columns ---
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        stats = df[num_cols].agg(["mean", "max", "min", "count", "std", "median"])
        # Convert numpy types to native Python for JSON serialization
        summary["numerical"] = {
            col: {stat: _safe_scalar(val) for stat, val in col_data.items()}
            for col, col_data in stats.to_dict().items()
        }
    else:
        summary["numerical"] = {}

    # --- Categorical columns ---
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    summary["categorical"] = {}
    for col in cat_cols:
        vc = df[col].value_counts()
        # Keep top 15 categories to avoid huge payloads
        summary["categorical"][col] = {
            str(k): int(v) for k, v in vc.head(15).items()
        }

    # --- Grouped relationships (Top categories vs Numerical means) ---
    summary["grouped_means"] = {}
    if len(num_cols) > 0 and len(cat_cols) > 0:
        # Limit to top 3 categorical and top 3 numerical to avoid token bloat
        top_cats = cat_cols[:3]
        top_nums = num_cols[:3]
        for cat in top_cats:
            # Get the top 10 most frequent items in this category
            top_cat_values = df[cat].value_counts().nlargest(10).index
            filtered_df = df[df[cat].isin(top_cat_values)]
            # Calculate the mean for these numerical columns
            grouped = filtered_df.groupby(cat)[top_nums].mean().round(2)
            summary["grouped_means"][cat] = grouped.to_dict()

    return summary


@st.cache_data
def get_data_quality_report(df):
    """
    Returns a data-quality report dictionary.

    Includes per-column missing percentage, total duplicates,
    and overall completeness score.
    """
    total_rows = len(df)
    missing_pct = ((df.isnull().sum() / total_rows) * 100).round(2).to_dict()
    duplicates = int(df.duplicated().sum())
    completeness = round((1 - df.isnull().sum().sum() / df.size) * 100, 2)

    return {
        "missing_percentage": missing_pct,
        "duplicate_rows": duplicates,
        "completeness_score": completeness,
        "total_cells": int(df.size),
        "total_missing_cells": int(df.isnull().sum().sum()),
    }


@st.cache_data
def get_correlation_matrix(df):
    """
    Computes the Pearson correlation matrix for numerical columns.

    Returns:
        pandas DataFrame (correlation matrix), or None if fewer than 2 numeric cols.
    """
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) < 2:
        return None
    return df[num_cols].corr().round(3)


@st.cache_data
def get_column_hints(df):
    """
    Generates human-readable hints about each column's role,
    useful as context for AI agents.

    Returns:
        dict mapping column name to a descriptive hint string.
    """
    hints = {}
    for col in df.columns:
        dtype = df[col].dtype
        nunique = df[col].nunique()
        total = len(df[col])
        missing = int(df[col].isnull().sum())

        if pd.api.types.is_numeric_dtype(dtype):
            hints[col] = (
                f"Numerical column with {nunique} unique values "
                f"(range {df[col].min()} – {df[col].max()}). "
                f"Missing: {missing}/{total}."
            )
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            hints[col] = (
                f"Date/time column spanning {df[col].min()} to {df[col].max()}. "
                f"Missing: {missing}/{total}."
            )
        else:
            # Treat as categorical / text
            top_val = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
            hints[col] = (
                f"Categorical/text column with {nunique} unique values. "
                f"Most frequent: '{top_val}'. Missing: {missing}/{total}."
            )
    return hints


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_scalar(val):
    """Convert numpy scalar to native Python type for JSON serialization."""
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return round(float(val), 4)
    return val
