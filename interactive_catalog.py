import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import lenscat
from lenscat.utils import *

st.title("Interactive Web App for lenscat")
# This catalog
catalog = lenscat.catalog

catalog_img = st.empty() # Placeholder

# Search by lens type
lens_type_option = st.multiselect(
    "Lens type",
    lenscat.Catalog._allowed_type
)
catalog = catalog.search(lens_type=lens_type_option)

# Write catalog
st.write(catalog.to_pandas())

# Plot catalog
plot_catalog(catalog)
catalog_img.image("catalog.png")