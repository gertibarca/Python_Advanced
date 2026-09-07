import streamlit as st

st.sidebar.header("sidebari")
st.sidebar.write("This is the sidebar")

st.button ("Click me")

if st.button ("butoni2"):
    st.success ("Operation was successful")

tab1, tab2, tab3 = st.tabs(["tab1","tab2","tab3"])

with tab1:
    st.header("Content of tab1")
    st.write("This is the content of tab1")

with tab2:
    st.header("Content of tab2")
    st.write("This is the content of tab2")

with tab3:
    st.header("Content of tab3")
    st.write("This is the content of tab3")