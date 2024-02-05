import streamlit as st
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import matplotlib
from matplotlib import pyplot as plt
import sys
import subprocess

_all = "all"

def convert_all_to_None(x):
    if x == _all:
        return None
    else:
        return x

def convert_to_zlens_range(zlens_min):
    if zlens_min is None or np.isclose(zlens_min, 0.0):
        return None # Do not filter
    else:
        return (zlens_min, np.inf)

st.set_page_config(
    page_title="Interactive Web App for lenscat",
    page_icon="https://avatars.githubusercontent.com/u/157114494?s=200&v=4",
    layout="centered",
    menu_items={
        "Report a bug": "https://github.com/lenscat/lenscat/issues",
        "About": "Interactive Web App for lenscat. See our GitHub repository [here](https://github.com/lenscat/lenscat).",
    },
)
st.markdown('''
<style>
.katex-html {
    text-align: left;
}
</style>''',
unsafe_allow_html=True
)
# Title
st.latex(r"{\Huge \texttt{lenscat}}")

# Upgrade to the latest release of lenscat
if "checked_update" not in st.session_state.keys():
    st.session_state["checked_update"] = False

if not st.session_state["checked_update"]:
    subprocess.run([f"{sys.executable}", "-m", "pip", "install", "lenscat", "--upgrade"])
    st.session_state["checked_update"] = True

import lenscat
from lenscat.utils import *
from lenscat._version import __version__
# This catalog
catalog = lenscat.catalog

catalog_img = st.empty() # Placeholder

expander = st.expander("Search/filter catalog", expanded=True)
# Search by RA
RA_range_option = expander.slider(
    "Right ascension [deg]",
    min_value=0,
    max_value=360,
    value=(0, 360),
    step=1,
    key="RA_range",
)
# Search by DEC
DEC_range_option = expander.slider(
    "Declination [deg]",
    min_value=-90,
    max_value=90,
    value=(-90, 90),
    step=1,
    key="DEC_range",
)
# Search by lens type
lens_type_option = expander.selectbox(
    "Lens type",
    (_all, *lenscat.Catalog._allowed_type),
    key="lens_type",
)
# Search by grading
grading_option = expander.selectbox(
    "Grading",
    (_all, *lenscat.Catalog._allowed_grading),
    key="grading",
)
# Search by lens redshift
zlens_min_option = expander.number_input(
    "Minimum lens redshift",
    min_value=0.0,
    value=0.0,
    step=0.1,
    key="zlens_min",
)
# Reset button
def reset():
    st.session_state.RA_range = (0, 360)
    st.session_state.DEC_range = (-90, 90)
    st.session_state.lens_type = _all
    st.session_state.grading = _all
    st.session_state.zlens_min = None
expander.button("Reset", type="primary", on_click=reset)

catalog = catalog.search(
    RA_range=RA_range_option,
    DEC_range=DEC_range_option,
    zlens_range=convert_to_zlens_range(zlens_min_option),
    grading=convert_all_to_None(grading_option),
    lens_type=convert_all_to_None(lens_type_option),
)

# Toggle for using hms instead of deg for RA
st.toggle(
    "Use hour-minute-second instead of degree for right ascension",
    value=False,
    key="use_hms_in_RA",
)

# Write catalog as an interactive table
catalog_df = catalog.to_pandas()
# NOTE Internally the catalog *always* uses degree
if st.session_state.use_hms_in_RA:
    sky_coord = SkyCoord(ra=catalog["RA"], dec=catalog["DEC"]) # Already with units
    catalog_df["RA"] = [c.split(' ')[0] for c in sky_coord.to_string('hmsdms')]
    catalog_df.rename(columns={"RA": "RA [hms]", "DEC": "DEC [deg]"}, inplace=True)
else:
    catalog_df.rename(columns={"RA": "RA [deg]", "DEC": "DEC [deg]"}, inplace=True)
st.dataframe(catalog_df, hide_index=True)

# Plot catalog
plot_catalog(catalog)
catalog_img.image("catalog.png")

# Footnote
st.caption("Using lenscat version "+__version__+". [GitHub repository for lenscat](https://github.com/lenscat/lenscat)")