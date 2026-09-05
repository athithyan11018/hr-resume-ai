import streamlit as st

from llm.ollama_client import generate_response


st.set_page_config(
    page_title="HR Resume AI",
    page_icon="🤖",
)

st.title("HR Resume AI Assistant")

st.write(
    "Ask questions about candidates and resumes."
)

query = st.text_area(
    "Enter your HR query",
    placeholder="Example: Find candidates with Python and Azure experience.",
)

if st.button("Ask AI"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            answer = generate_response(query)

        st.subheader("AI Response")
        st.write(answer)