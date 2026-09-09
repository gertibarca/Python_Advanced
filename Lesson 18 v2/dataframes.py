import pandas as pd
import streamlit as st

st.header("Displaying DataFrames")

data = pd.DataFrame({
    "Name": ["Gerti", "Geati", "Adonisi"],
    "Age": [16, 13, 17]
})

st.dataframe(data)
