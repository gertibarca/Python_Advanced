import pandas as pd
import streamlit as st
import plotly.express as px


books_df = pd.read_csv("bestsellers_with_categories_2022_03_27.csv")

st.title("Best Selling Books Analysis")
st.write("This app analyses the Amazon top selling books from 2009-2022")

st.subheader("Summary Statistics")

total_books = books_df.shape[0]
unique_titles = books_df["Name"].nunique()
avg_rating = books_df["User Rating"].mean()
avg_price = books_df["Price"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Books", total_books)
col2.metric("Unique Titles", unique_titles)
col3.metric("Average Rating", f"{avg_rating:.2f}")
col4.metric("Average Price", f"${avg_price:.2f}")

st.subheader("Data Set Preview")
st.write(books_df.head())

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Book Titles")
    top_titles = books_df["Name"].value_counts().head(10)
    st.bar_chart(top_titles)

with col2:
    st.subheader("Top 10 Authors")
    top_authors = books_df["Author"].value_counts().head(10)
    st.bar_chart(top_authors)

st.subheader("Genres")

genre_counts = books_df["Genre"].value_counts()

fig = px.pie(
    values=genre_counts.values,
    names=genre_counts.index,
    title="Preferred Genres"
)

st.plotly_chart(fig, use_container_width=True)
