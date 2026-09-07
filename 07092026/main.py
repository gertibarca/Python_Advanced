import streamlit as st

st.title ("Hello")

st.button ("Click me")

if st.button ("hello"):
    st.write ("Butoni eshte klikuar")

if st.button ("butoni3"):
    st.success ("Operation was successful")