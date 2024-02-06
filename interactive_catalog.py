import streamlit as st
import numpy as np
import pandas as pd
from datetime import time, timedelta
from astropy.coordinates import SkyCoord
import matplotlib
from matplotlib import pyplot as plt
import sys
import subprocess

_all = "all"
_RA_default_range_deg = (0, 360)
_RA_default_range_hms = (time.min, time.max)

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
st.caption("A public and community-contributed catalog of known strong gravitational lenses.")

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
# Record the total number of entries
st.session_state["nentries"] = len(catalog)

catalog_img = st.empty() # Placeholder

# Toggle for using hms instead of deg for RA
st.toggle(
    "Use hour-minute-second instead of degree for right ascension",
    value=False,
    key="use_hms_in_RA",
)

if "RA_range" not in st.session_state.keys():
    st.session_state["RA_range"] = _RA_default_range_deg # Internally always use deg

def convert_time_to_hms_str(t):
    hms_str = "{}h{}m{}.{}s".format(
        str(t.hour).zfill(2),
        str(t.minute).zfill(2),
        str(t.second).zfill(2),
        str(t.microsecond).zfill(6),
    )

    return hms_str

def update_RA_range(key, format):
    RA_range = st.session_state[key]
    if format == "deg":
        st.session_state["RA_range"] = RA_range # No change is needed
    elif format == "hms":
        RA_min = convert_time_to_hms_str(RA_range[0])
        RA_max = convert_time_to_hms_str(RA_range[1])
        _sky_coord = SkyCoord(ra=[RA_min, RA_max], dec=['00h00m00s', '00h00m00s'])
        st.session_state["RA_range"] = (_sky_coord[0].ra.value, _sky_coord[1].ra.value)
    else:
        raise ValueError(f"Does not understand {format}")

expander = st.expander("Search/filter catalog", expanded=True)
# Search by RA
RA_slider = expander.empty()
if st.session_state["use_hms_in_RA"] == False:
    RA_slider.slider(
        "Right ascension [deg]",
        min_value=_RA_default_range_deg[0],
        max_value=_RA_default_range_deg[1],
        value=_RA_default_range_deg,
        step=1,
        key="RA_range_deg",
        on_change=update_RA_range,
        args=("RA_range_deg", "deg"),
    )
else:
    RA_slider.slider(
        "Right ascension [hms]",
        value=_RA_default_range_hms,
        step=timedelta(minutes=15),
        format="HH[h]mm[m]ss[s]",
        key="RA_range_hms",
        on_change=update_RA_range,
        args=("RA_range_hms", "hms")
    )
    # Update *internally* 
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
    st.session_state["RA_range"] = (0, 360)
    if "RA_range_deg" in st.session_state.keys():
        st.session_state["RA_range_deg"] = _RA_default_range_deg
    if "RA_range_hms" in st.session_state.keys():
        st.session_state["RA_range_hms"] = _RA_default_range_hms
    st.session_state.DEC_range = (-90, 90)
    st.session_state.lens_type = _all
    st.session_state.grading = _all
    st.session_state.zlens_min = None
expander.button("Reset", type="primary", on_click=reset)

catalog = catalog.search(
    RA_range=st.session_state["RA_range"],
    DEC_range=DEC_range_option,
    zlens_range=convert_to_zlens_range(zlens_min_option),
    grading=convert_all_to_None(grading_option),
    lens_type=convert_all_to_None(lens_type_option),
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
st.dataframe(
    catalog_df,
    hide_index=True,
)
st.caption("Matched {}/{} entries in the catalog".format(len(catalog_df), st.session_state["nentries"]))

from streamlit_javascript import st_javascript
st_theme = st_javascript("""window.getComputedStyle(window.parent.document.getElementsByClassName("stApp")[0]).getPropertyValue("color-scheme")""")
st.write(f"Currently using the {st_theme} mode")

# Plot catalog
plot_catalog(catalog)
catalog_img.image("catalog.png")

st.divider()
# Footnote
st.caption("Using lenscat version "+__version__+". [GitHub repository for lenscat](https://github.com/lenscat/lenscat)")