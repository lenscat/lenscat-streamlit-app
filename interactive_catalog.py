import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import lenscat
from lenscat.utils import *
from lenscat._version import __version__

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
# This catalog
catalog = lenscat.catalog

catalog_img = st.empty() # Placeholder

# Search by RA
RA_range = st.slider(
    "Right ascension [deg]",
    min_value=0,
    max_value=360,
    value=(0, 360),
    step=1,
)
# Search by DEC
DEC_range = st.slider(
    "Declination [deg]",
    min_value=-90,
    max_value=90,
    value=(-90, 90),
    step=1,
)
# Search by lens type
lens_type_option = st.selectbox(
    "Lens type",
    (_all, *lenscat.Catalog._allowed_type),
)
# Search by grading
grading_option = st.selectbox(
    "Grading",
    (_all, *lenscat.Catalog._allowed_grading),
)
# Search by lens redshift
zlens_min = st.number_input(
    "Minimum lens redshift",
    min_value=0.0,
    value=None,
    step=0.1,
)
catalog = catalog.search(
    RA_range=RA_range,
    DEC_range=DEC_range,
    zlens_range=convert_to_zlens_range(zlens_min),
    grading=convert_all_to_None(grading_option),
    lens_type=convert_all_to_None(lens_type_option),
)

# Write catalog as an interactive table
st.dataframe(catalog.to_pandas(), hide_index=True)

# Plot catalog
plot_catalog(catalog)
catalog_img.image("catalog.png")

# Print version
st.caption("lenscat version "+__version__)