import streamlit as st
import httpx
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

st.title("AI Code Review")

code = st.text_area("Paste your code here", height=300)
language = st.selectbox("Select language (optional)", ["None", "Python", "JavaScript", "Java", "C++"])
if st.button("Analyze"):
    if not code:
        st.error("Please enter some code")
    else:
        with st.spinner("Analyzing..."):
            try:
                response = httpx.post(
                    f"{BACKEND_URL}/analyze",
                    json={"code": code, "language": language if language != "None" else None},
                    timeout=30
                )
                response.raise_for_status()
                feedback = response.json()["markdown_feedback"]
                st.markdown(feedback)
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")
st.write("For GitHub PR integration, configure a webhook pointing to `<your-domain>/api/webhook`")
