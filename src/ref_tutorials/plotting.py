"""Publication-quality plotting helpers.

These helpers keep figures consistent across the training notebooks and give
readers a recipe they can copy into their own work.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

#: matplotlib rcParams applied by :func:`set_publication_style`.
PUBLICATION_RCPARAMS = {
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "legend.frameon": False,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
}


def set_publication_style() -> None:
    """Apply a consistent, publication-quality matplotlib style.

    Updates the global :data:`matplotlib.rcParams` with
    :data:`PUBLICATION_RCPARAMS`. Call this once near the top of a notebook.
    """
    plt.rcParams.update(PUBLICATION_RCPARAMS)


def model_comparison_figure(
    df: pd.DataFrame,
    *,
    value_col: str = "value",
    model_col: str = "source_id",
    group_col: str | None = None,
    title: str | None = None,
    ylabel: str | None = None,
) -> tuple[Figure, plt.Axes]:
    """Build a multi-model comparison figure for a scalar metric.

    Produces a horizontal bar chart with one bar per model, sorted by value.
    When ``group_col`` is given, models with several entries (for example
    multiple ensemble members) are aggregated to their mean and the spread is
    drawn as an error bar.

    Parameters
    ----------
    df
        Tidy DataFrame, e.g. from :func:`ref_tutorials.metric_values_to_dataframe`.
    value_col
        Column holding the scalar metric value.
    model_col
        Column identifying the model.
    group_col
        Optional extra column to aggregate within (alongside ``model_col``).
    title
        Optional figure title.
    ylabel
        Optional label for the value axis. Defaults to ``value_col``.

    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        The created figure and axes, so the caller can tweak them further.
    """
    keys = [model_col] if group_col is None else [model_col, group_col]
    grouped = df.groupby(keys)[value_col]
    summary = grouped.mean().to_frame("mean")
    summary["spread"] = grouped.std().fillna(0.0)
    summary = summary.reset_index().sort_values("mean")

    labels = (
        summary[model_col].astype(str)
        if group_col is None
        else summary[model_col].astype(str) + " / " + summary[group_col].astype(str)
    )

    fig, ax = plt.subplots(figsize=(7, 0.4 * len(summary) + 1.5))
    ax.barh(
        labels,
        summary["mean"],
        xerr=summary["spread"],
        color="#1f77b4",
        error_kw={"ecolor": "#444444", "capsize": 3},
    )
    ax.set_xlabel(ylabel or value_col)
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig, ax


def save_figure(fig: Figure, path: str | Path) -> list[Path]:
    """Save a figure in publication-ready formats.

    Writes both a ``.png`` (for quick viewing) and a ``.pdf`` (vector, for
    papers) next to ``path``, regardless of the suffix passed in.

    Parameters
    ----------
    fig
        The figure to save.
    path
        Target path; its suffix is ignored and replaced.

    Returns
    -------
    list[pathlib.Path]
        The paths actually written.
    """
    base = Path(path)
    written = []
    for suffix in (".png", ".pdf"):
        out = base.with_suffix(suffix)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out)
        written.append(out)
    return written
