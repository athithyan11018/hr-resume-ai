import streamlit as st

st.title("HR Resume AI Assistant")

st.write("Local AI resume assistant")

query = st.text_input(
    "Ask an HR question",
    placeholder="Find candidates with Python and Azure..."
)

if query:
    st.write("Your query:", query)