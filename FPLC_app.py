"""
FPLC_app.py

Streamlit app for generating FPLC chromatogram plots. Upload a csv, adjust
plot parameters in the sidebar, download the resulting png.

Run locally with:  streamlit run FPLC_app.py
"""

import io

import pandas as pd
import streamlit as st

from FPLC_plotting import load_fplc_data, make_fplc_plot

st.set_page_config(page_title="FPLC Plotting", layout="wide")
st.title("FPLC Chromatogram Plotting")

uploaded_file = st.file_uploader("Upload FPLC csv export", type=["csv"])

if uploaded_file is None:
    st.info("Upload a csv file to get started. It may take a moment to render, but should then update live as you adjust the plot.")
    st.stop()

# Parsing errors (wrong file format, unexpected columns, etc.) are common
# with real lab data, so surface a readable message instead of a raw traceback.
try:
    data = load_fplc_data(uploaded_file.getvalue())
except Exception as e:
    st.error(f"Couldn't parse this csv - is it a raw FPLC export? Details: {e}")
    st.stop()

default_title = f"{uploaded_file.name.rsplit('.', 1)[0]}_FPLC"

## plot customization options 
st.sidebar.header("FPLC Plot Customization")

## title 
plot_title = st.sidebar.text_input("Plot title", value=default_title)

## axes options 
with st.sidebar.expander("Axes ranges"):
    use_custom_range = st.checkbox("Zoom to custom mL range or mAU height", value=False)
    if use_custom_range:
        full_min = float(data["uv_cond_df"]["ml"].min())
        full_max = float(data["uv_cond_df"]["ml"].max())
        col1, col2 = st.columns(2)
        ml_start = col1.number_input("mL start", value=full_min)
        ml_end = col2.number_input("mL end", value=full_max)
        use_custom_height = st.checkbox("Set a fixed UV (mAU) axis height", value=False)
        mAU_height = st.number_input("mAU height", min_value=1.0, value=1750.0) if use_custom_height else None
    else:
        ml_start, ml_end, mAU_height = None, None, None

## traces 
with st.sidebar.expander("Traces"):
    show_cond = st.checkbox("Conductivity", value=True)
    show_gradient = st.checkbox("%B gradient", value=False)

## annotations 
with st.sidebar.expander("Annotations"):
    show_peak_labels = st.checkbox("Peak labels", value=False)
    if show_peak_labels:
        st.caption("Add rows for each peak you want labeled.")
        peak_df = st.data_editor(
            pd.DataFrame([{"label": "dimer", "mL": 110}, {"label": "TigE", "mL": 150}]),
            num_rows="dynamic",
            key="peak_editor",
        )
        peak_labels = {
            i: {"mL": row["mL"], "label": row["label"]}
            for i, row in enumerate(peak_df.to_dict("records"))
            if pd.notna(row.get("mL")) and row.get("label")
        }
        peak_label_offset = st.number_input("Peak label offset (%)", min_value=-100.0, max_value=100.0, value=7.5, step=1.0)
        find_peak_max = st.checkbox("Snap peak labels to nearest local max", value=True)
        peak_snap_window = st.number_input("Within x mL of input", min_value=1,value=10, step=1) if find_peak_max else 0
    else:
        peak_labels = {}
        find_peak_max = False
        peak_snap_window = 10
        peak_label_offset = 7.5
    show_step_labels = st.checkbox("Step labels", value=False)
    if show_step_labels:
        st.caption("Add rows for each step you want labeled, start mL assumed as end of the prior step (or start of file).")
        step_df = st.data_editor(
            pd.DataFrame(
                [
                    {"label": "Equil", "end_mL": -25},
                    {"label": "Wash", "end_mL": 25},
                    {"label": "Elute", "end_mL": 140},
                ]
            ),
            num_rows="dynamic",
            key="step_editor",
        )
        step_labels = {
            i: {"end_mL": row["end_mL"], "label": row["label"]}
            for i, row in enumerate(step_df.to_dict("records"))
            if pd.notna(row.get("end_mL")) and row.get("label")
        }
    else: 
        step_labels = {}

## fractions and highlighting 
with st.sidebar.expander("Fractions and highlighting"):
    show_frac_lines = st.checkbox("Fraction lines", value=False)
    show_frac_highlights = st.checkbox("Highlight a fraction range", value=False)
    frac_first = frac_last = None
    if show_frac_highlights:
        col1, col2 = st.columns(2)
        frac_first = col1.number_input("First fraction", value=16, step=1)
        frac_last = col2.number_input("Last fraction", value=23, step=1)
    show_gel = st.checkbox("Highlight gel sample fractions", value=False)
    gel_samples = []
    if show_gel:
        gel_input = st.text_input("Gel sample fractions (comma-separated)", value="9")
        gel_samples = [int(x.strip()) for x in gel_input.split(",") if x.strip()]

## colors and figure size
with st.sidebar.expander("Colors and size"):
    color_uv = st.color_picker("UV color", value="#1f77b4")
    color_cond = st.color_picker("Conductivity color", value="#ff7f0e")
    color_gradient = st.color_picker("%B gradient color", value="#2ca02c")
    color_frac = st.color_picker("Fraction color", value="#2ca02c")
    color_gel = st.color_picker("Gel sample color", value="#c9a339")
    fig_width = st.number_input("Figure width", min_value=2.0, max_value=30.0, value=8.0)
    fig_height = st.number_input("Figure height", min_value=2.0, max_value=30.0, value=5.0)

fig = make_fplc_plot(
    data,
    title=plot_title,
    ml_start=ml_start,
    ml_end=ml_end,
    mAU_height=mAU_height,
    show_cond=show_cond,
    show_gradient=show_gradient,
    show_peak_labels=show_peak_labels,
    show_step_labels=show_step_labels,
    show_frac_lines=show_frac_lines,
    show_frac_highlights=show_frac_highlights,
    show_gel=show_gel,
    find_peak_max=find_peak_max,
    peak_snap_window=peak_snap_window,
    peak_labels=peak_labels,
    peak_label_offset=peak_label_offset,
    step_labels=step_labels,
    frac_first=frac_first,
    frac_last=frac_last,
    gel_samples=gel_samples,
    color_uv=color_uv,
    color_cond=color_cond,
    color_gradient=color_gradient,
    color_frac=color_frac,
    color_gel=color_gel,
    fig_width=fig_width,
    fig_height=fig_height,
)

st.pyplot(fig)

png_buffer = io.BytesIO()
fig.savefig(png_buffer, format="png", dpi=300)
st.download_button(
    "Download plot as PNG",
    data=png_buffer.getvalue(),
    file_name=f"{plot_title}.png",
    mime="image/png",
)
