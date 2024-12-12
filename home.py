import streamlit as st

st.set_page_config(page_title="Welcome", layout="centered")

# Title at the top of the page
st.markdown(
    '<h1 class="main-title">Welcome to Instructional Quality Agent (IQA) Prototype</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    """Refine your course content effortlessly in just 10-15 minutes.
            Upload your materials (PDF, MP3, MP4, or YouTube link) to get actionable feedback on design, transferability, and performance. Your input is private and securely analyzed using advanced AI insights.
            Inspired by cutting-edge instructional frameworks, this tool empowers educators to deliver exceptional learning experiences.
            Built to support your success—contact us for feedback or to customize a solution for your needs."""
)


# Create columns for prompts
col1, col2, col3, col4 = st.columns(4)


with col1:
    st.button("Evaluate a sales course")
    # st.session_state["starter_prompt"] = "Evaluate a sales course"


with col2:
    st.button("Assess onboarding material")
    # st.session_state["starter_prompt"] = "Assess onboarding material"


with col3:
    st.button("Review compliance training")
    # st.session_state["starter_prompt"] = "Review compliance training"

with col4:
    st.button("Analyze leadership workshop")
    # st.session_state["starter_prompt"] = "Analyze leadership workshop"


col = st.columns(3)[1]
with col:
    st.markdown("\n\n")
    st.page_link("pages/app.py", label="Let's Start", icon=":material/send:")
