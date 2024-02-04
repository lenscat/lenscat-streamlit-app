import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import lenscat
from lenscat.utils import *

_all = "all"

def convert_all_to_None(x):
    if x == _all:
        return None
    else:
        return x

st.title("Interactive Web App for lenscat")
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
catalog = catalog.search(
    RA_range=RA_range,
    DEC_range=DEC_range,
    grading=convert_all_to_None(grading_option),
    lens_type=convert_all_to_None(lens_type_option),
)

# Write catalog
st.write(catalog.to_pandas())

# Plot catalog
plot_catalog(catalog)
catalog_img.image("catalog.png")