import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import sys
import subprocess
import importlib

_all = "all"

def convert_all_to_None(x):
    if x == _all:
        return None
    else:
        return x

def convert_to_zlens_range(zlens_min):
    if zlens_min is None:
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
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lenscat', '--upgrade'])

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
    value=None,
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

# Write catalog as an interactive table
st.dataframe(catalog.to_pandas(), hide_index=True)

# Plot catalog
plot_catalog(catalog)
catalog_img.image("catalog.png")

# Footnote
st.caption("Using lenscat version "+__version__+". [GitHub repository for lenscat](https://github.com/lenscat/lenscat)")