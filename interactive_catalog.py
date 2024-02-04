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
    grading=convert_all_to_None(grading_option),
    lens_type=convert_all_to_None(lens_type_option),
)

# Write catalog
st.write(catalog.to_pandas())

# Plot catalog
plot_catalog(catalog)
catalog_img.image("catalog.png")