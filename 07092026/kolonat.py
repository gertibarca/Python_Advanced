import streamlit as st

col1, col2, col3, col4, col5 = st.columns(5,ga0p="small")

with col1:
    st.header("Hello there")

with col2:
    st.header("this is column 2")
    st.button("click me")

with col3:
    st.header("this is column 3")

with col4:
    st.header("this is column 4")

with col5:
    st.header("this is column 5")
