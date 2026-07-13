"""
FPLC_plotting.py

Shared data-loading and plotting logic for FPLC chromatogram plots.
Used by both the FPLC_plotting.ipynb notebook (for interactive/exploratory
use) and FPLC_app.py (the Streamlit app for the rest of the lab).

requirements: pandas, matplotlib
"""

import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.weight"] = "bold"  # Bolds general text (titles, etc.)
plt.rcParams["axes.labelweight"] = "bold"  # Bolds x and y axis labels


def load_fplc_data(csv_source):
    """
    Load and clean a raw FPLC export csv.

    csv_source: either a path to the csv file (str or Path), or raw bytes
    (e.g. from a Streamlit file uploader's .getvalue()). The file gets read
    several times over the course of parsing, which is why bytes are handled
    explicitly here rather than a single file-like object (which could only
    be read once without extra seek bookkeeping).

    Returns a dict with:
        uv_cond_df    - DataFrame with columns "ml", "mAU", and (if present) "mS/cm"
        injection_df  - DataFrame with the injection column (not yet used in plotting)
        fractions_df  - DataFrame with fraction mL positions and fraction numbers
        concB_df      - DataFrame with %B gradient data
        is_method_run - bool, True if this was a method run (vs. manual run),
                        which determines which columns hold fraction data
    """
    # The file has 2 rows to ignore at the top, then one header row,
    # then the data starts at row 4 (0-indexed row 3).

    # read UV and conductance data (they use the same mL values in csv for x axis)
    uv_cond_raw = pd.read_csv(
        _reader(csv_source),
        sep="\t",
        header=2,
        usecols=[0, 1, 3],
        engine="python",
        encoding="utf-16",
        na_values=["", '""'],
    )

    # find injection (todo to be implemented)
    injection_raw = pd.read_csv(
        _reader(csv_source),
        sep="\t",
        header=2,
        usecols=[6],
        nrows=1,
        engine="python",
        encoding="utf-16",
        na_values=["", '""'],
    )

    # read fraction data (and check if method run or manual run)
    is_method_run = _is_method_run(csv_source)
    fractions_raw = pd.read_csv(
        _reader(csv_source),
        sep=r"\t",  # whitespace sep (tabs + spaces)
        header=2,  # header row to parse
        usecols=[10, 11] if is_method_run else [8, 9],  # mL and fraction# columns
        engine="python",
        encoding="utf-16",
        na_values=["", '""'],
    )

    # read %B conc
    concB_raw = pd.read_csv(
        _reader(csv_source),
        sep="\t",
        header=2,
        usecols=[4, 5],
        engine="python",
        encoding="utf-16",
        na_values=["", '""'],
    )

    # clean text in "fraction" column
    fractions_raw["Fraction"] = (
        fractions_raw["Fraction"].astype(str).str.replace(r"[^\d\-]", "", regex=True)
    )

    # convert to numeric
    uv_cond_df = uv_cond_raw.apply(pd.to_numeric, errors="coerce")
    injection_df = injection_raw.apply(pd.to_numeric, errors="coerce")
    fractions_df = fractions_raw.apply(pd.to_numeric, errors="coerce")
    concB_df = concB_raw.apply(pd.to_numeric, errors="coerce")

    return {
        "uv_cond_df": uv_cond_df,
        "injection_df": injection_df,
        "fractions_df": fractions_df,
        "concB_df": concB_df,
        "is_method_run": is_method_run,
    }


def _reader(csv_source):
    """Return something pd.read_csv can read fresh, whether given a path or raw bytes."""
    if isinstance(csv_source, (bytes, bytearray)):
        return io.BytesIO(csv_source)
    return csv_source  # path-like (str/Path) - pd.read_csv reopens it each call


def _is_method_run(csv_source):
    """Check the 3rd line of the file for 'Logbook' to determine manual vs method run."""
    if isinstance(csv_source, (bytes, bytearray)):
        lines = csv_source.decode("utf-16").splitlines(keepends=True)[:3]
    else:
        with open(csv_source, encoding="utf-16") as f:
            lines = [f.readline() for _ in range(3)]
    return "Logbook" in lines[2]


def make_fplc_plot(
    data,
    title,
    ml_start=None,
    ml_end=None,
    mAU_height=None,
    show_cond=False,
    show_gradient=True,
    show_peak_labels=True,
    show_step_labels=True,
    show_frac_lines=False,
    show_frac_highlights=False,
    show_gel=False,
    find_peak_max=True,
    peak_snap_window=10,
    peak_labels=None,
    peak_label_offset=7.5,
    step_labels=None,
    frac_first=None,
    frac_last=None,
    gel_samples=None,
    color_uv="tab:blue",
    color_cond="tab:orange",
    color_gradient="tab:green",
    color_frac="tab:green",
    color_gel="xkcd:mustard yellow",
    fig_width=8.0,
    fig_height=5.0,
):
    """
    Build an FPLC chromatogram plot (matplotlib Figure) from loaded data.

    `data` is the dict returned by load_fplc_data().

    Leaving ml_start/ml_end/mAU_height as None reproduces the original "full
    plot" behavior (full data range, auto y-axis). Setting them reproduces
    the original "zoomed plot" behavior. show_frac_lines / show_frac_highlights
    / show_gel default to off, matching the original full plot; turn them on
    (and set frac_first/frac_last/gel_samples) for the zoomed-plot style view.

    peak_labels and step_labels are dicts of dicts, e.g.:
        peak_labels = {1: {"mL": 10, "label": "wash"}, ...}
        step_labels = {1: {"end_mL": -25, "label": "Equil"}, ...}
    """
    peak_labels = peak_labels or {}
    step_labels = step_labels or {}
    gel_samples = gel_samples or []

    uv_cond_df = data["uv_cond_df"]
    concB_df = data["concB_df"]
    fractions_df = data["fractions_df"]
    is_method_run = data["is_method_run"]

    x_uv_cond = uv_cond_df["ml"]
    y_uv = uv_cond_df["mAU"]
    y_cond = uv_cond_df["mS/cm"] if "mS/cm" in uv_cond_df.columns else None
    x_gradient = concB_df["ml.2"]
    y_gradient = concB_df["%B"]

    effective_ml_start = ml_start if ml_start is not None else float(x_uv_cond.min())
    effective_ml_end = ml_end if ml_end is not None else float(x_uv_cond.max())

    fig, ax1 = plt.subplots(figsize=(fig_width, fig_height))

    # set axes
    ax1.set_xlabel("Volume (mL)")
    ax1.set_ylabel("UV (mAU)", color=color_uv)
    if ml_start is not None or ml_end is not None:
        ax1.set_xlim(effective_ml_start, effective_ml_end)
    if mAU_height is not None:
        ax1.set_ylim(0, mAU_height)

    # plot uv
    ax1.plot(x_uv_cond, y_uv, color=color_uv, linewidth=1)
    ax1.tick_params(axis="y", colors=color_uv)

    # plot conductance
    if show_cond and y_cond is not None:
        ax2 = ax1.twinx()
        ax2.set_ylabel("Conductivity (mS/cm)", color=color_cond)
        ax2.plot(x_uv_cond, y_cond, color=color_cond, linewidth=0.5, linestyle="-")
        ax2.tick_params(axis="y", colors=color_cond)

    # plot %B gradient
    if show_gradient:
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("axes", 1.15 if show_cond else 1.0))
        ax3.set_ylabel("%B", color=color_gradient)
        ax3.plot(x_gradient, y_gradient, color=color_gradient, linewidth=0.5, linestyle="-")
        ax3.tick_params(axis="y", colors=color_gradient)

    # display peak labels
    if show_peak_labels and peak_labels:
        tol = 0.5  # tolerance in mL for matching mL inputs with uv_cond_df x values
        for peak in peak_labels.values():
            target_ml = peak["mL"]
            match_idx = None

            if find_peak_max:
                # find uv_cond_df index of the closest x value to the requested mL input
                target_idx = None
                min_diff = None
                for i, x_val in enumerate(x_uv_cond):
                    diff = abs(float(x_val) - target_ml)
                    if diff < tol and (min_diff is None or diff < min_diff):
                        min_diff = diff
                        target_idx = i

                if target_idx is None:
                    continue

                # search a small neighborhood around target_idx for the local maximum
                # convert the search window from mL to a row count, using the
                # (roughly constant) mL spacing between data points, so the
                # window means the same physical distance regardless of sampling density
                ml_per_point = (x_uv_cond.iloc[-1] - x_uv_cond.iloc[0]) / (len(x_uv_cond) - 1)
                search_range = max(1, int(round(peak_snap_window / ml_per_point)))                
                start = max(0, target_idx - search_range)
                end = min(len(y_uv) - 1, target_idx + search_range)
                local_slice = y_uv.iloc[start : end + 1]
                peak_idx = local_slice.idxmax()
                match_idx = int(peak_idx)
            else:
                # use the exact requested mL input
                for i, x_val in enumerate(x_uv_cond):
                    if abs(float(x_val) - target_ml) < tol:
                        match_idx = i
                        break

            if match_idx is None:
                continue

            x_peak = x_uv_cond.iloc[match_idx]
            y_peak = y_uv.iloc[match_idx]

            label_x = x_peak + peak_label_offset / 100 * (effective_ml_end - effective_ml_start)
            label_y = min(max(y_peak, ax1.get_ylim()[1] * 0.2), ax1.get_ylim()[1] * 0.9)  # label y position within 20-90% of y axis range

            ax1.annotate(
                peak["label"],
                xy=(x_peak, y_peak),
                xytext=(label_x, label_y),
                textcoords="data",
                ha="center",
                va="center",
                fontsize=10,
                annotation_clip=False
            )

    # display step labels
    if show_step_labels and step_labels:
        start_ml = effective_ml_start
        step_label_offset = -0.03 * fig_height
        step_label_bottom_bracket = step_label_offset - 0.01 * fig_height
        for step in step_labels.values():
            end_ml = step["end_mL"]
            label = step["label"]

            start_x = x_uv_cond.iloc[(x_uv_cond - start_ml).abs().idxmin()]
            end_x = x_uv_cond.iloc[(x_uv_cond - end_ml).abs().idxmin()]

            # start bracket
            if start_ml > effective_ml_start and start_ml < effective_ml_end:
                ax1.plot(
                    [start_x, start_x],
                    [step_label_offset, step_label_bottom_bracket],
                    transform=ax1.get_xaxis_transform(),
                    color="black",
                    lw=0.8,
                    clip_on=False,
                )
            # end bracket
            if end_ml < effective_ml_end and end_ml > effective_ml_start:
                ax1.plot(
                    [end_x, end_x],
                    [step_label_offset, step_label_bottom_bracket],
                    transform=ax1.get_xaxis_transform(),
                    color="black",
                    lw=0.8,
                    clip_on=False,
                )
            # line connecting start and end brackets
            if max(start_x, effective_ml_start) < min(end_x, effective_ml_end):
                ax1.plot(
                    [max(start_x, effective_ml_start), min(end_x, effective_ml_end)],
                    [step_label_bottom_bracket, step_label_bottom_bracket],
                    transform=ax1.get_xaxis_transform(),
                    color="black",
                    lw=0.8,
                    clip_on=False,
                )
                ax1.text(
                    (max(start_x, effective_ml_start) + min(end_x, effective_ml_end)) / 2,
                    step_label_bottom_bracket - 0.04,
                    label,
                    transform=ax1.get_xaxis_transform(),
                    ha="center",
                    va="top",
                    fontsize=9,
                    color="black",
                    clip_on=False,
                )
            start_ml = end_ml

    # fraction column depends on manual vs method run; needed for fraction
    # lines and/or gel highlighting
    frac_col = "ml.5" if is_method_run else "ml.4"

    # plot fractions
    if show_frac_lines:
        for ml, frac in zip(fractions_df[frac_col], fractions_df["Fraction"]):
            if effective_ml_start < ml < effective_ml_end:
                ax1.axvline(x=ml, color=color_frac, linestyle="-", linewidth=0.8, ymin=0, ymax=0.1)
                ax1.text(
                    ml,
                    ax1.get_ylim()[1] * 0.11,
                    f"{frac:.0f}",
                    rotation=90,
                    va="bottom",
                    ha="center",
                    fontsize=8,
                    color=color_frac,
                    fontweight="normal",
                )

    # shade the selected fraction range (frac_first...frac_last) under UV curve
    if show_frac_highlights and frac_first is not None and frac_last is not None:
        x_min = fractions_df.loc[fractions_df["Fraction"] == frac_first, frac_col].iloc[0]
        x_max = fractions_df.loc[fractions_df["Fraction"] == frac_last + 1, frac_col].iloc[0]
        mask = (x_uv_cond >= x_min) & (x_uv_cond <= x_max)
        ax1.fill_between(x_uv_cond[mask], y_uv[mask], color=color_frac, alpha=0.15)

    # plot gel samples (independent of show_frac_lines, matching original intent)
    if show_gel and len(gel_samples) > 0:
        for gel_frac in gel_samples:
            x_min = fractions_df.loc[fractions_df["Fraction"] == gel_frac, frac_col].iloc[0]
            x_max = fractions_df.loc[fractions_df["Fraction"] == gel_frac + 1, frac_col].iloc[0]
            mask = (x_uv_cond >= x_min) & (x_uv_cond <= x_max)
            ax1.fill_between(x_uv_cond[mask], y_uv[mask], color=color_gel, alpha=0.25)

    plt.title(title)
    fig.tight_layout()

    return fig
