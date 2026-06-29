import streamlit as st

st.sidebar.header("Sidebar")
st.sidebar.write("This is inside the sidebar")

st.sidebar.selectbox("chose an option", ["Option 1", "Option 2","Option 3"])