import streamlit as st
import pandas as pd
import sys

sys.path.append("src")
from utils import get_client
from vector_search import vector_search

df = pd.read_csv("./data/books.csv", usecols=["bookId", "coverImg"]).set_index("bookId")

st.title("Book Recommendation System :books:")
st.write("This app recommends books based on a search query.")

# get user input
form = st.form(key="book-search")
query = form.text_input(
    label="In a few words, describe the type of books you're looking for (e.g., 'adventure novel with some philosophy'):"
)
submit = form.form_submit_button(label="Submit")

if submit:
    # get client
    client = get_client(openai=True)

    # get recommendations
    recommendations = vector_search(client, query)

    if len(recommendations) == 0 or recommendations is None:
        st.write(
            "No recommendations were found for your search query; please try another one!"
        )
    else:
        # display top three recommendations
        for book in recommendations[:3]:
            image_col, text_col = st.columns([1, 3])

            book_id = book["bookId"]
            cover_img = df.loc[book_id]["coverImg"]
            with image_col:
                st.image(cover_img, width=150)
            with text_col:
                # details
                st.write(
                    f':gray[DISTANCE SCORE: {book["_additional"]["distance"]:0.4f}]'
                )
                st.write(f'TITLE: {book["title"]}')
                st.write(f'DESCRIPTION: {book["description"]}')
            st.write("---")
