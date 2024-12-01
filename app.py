import streamlit as st

# Set page configuration
st.set_page_config(page_title="Instructional Quality Prototype", layout="centered")

# Sidebar: File Upload
st.sidebar.title("Upload Your Course Materials")
uploaded_file = st.sidebar.file_uploader("Upload your course materials:", type=["pdf", "mp3", "mp4"])
if uploaded_file:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    st.session_state["uploaded_file"] = uploaded_file
else:
    st.sidebar.info("Please upload your course materials here.")
#     st.stop()

# Sidebar: Instructions
st.sidebar.title("Instructions")
st.sidebar.markdown(
    """
    ### How to Use:
    1. **Attach Course Files**: 
       - Upload the course files you want evaluated (PDFs, YouTube links, or audio files).
    2. **Verification and Preferences**: 
       - I will verify the course structure and categories, and confirm the level of critique you prefer.
    3. **Evaluation Frameworks**: 
       - I will evaluate your course using various proven frameworks.
    4. **Summarized Results**: 
       - At the end, you will receive a summary with ratings and actionable insights.
    5. **Downlaodable Report**:
       - You can download the report for further analysis or sharing.
    """
)


# Custom CSS to modify sidebar and page layout
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        width: 250px;
    }
    .main-title {
        text-align: center;
        font-size: 2.5em;
        color: #2c3e50;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Title at the top of the page
st.markdown('<h1 class="main-title">Instructional Quality Prototype (IQA)</h1>', unsafe_allow_html=True)
st.markdown(
    """
    Welcome to the Instructional Quality Prototype.  I am your virtual IQP guide or co-researcher and I’ll be walking you through a variety of steps to evaluate your course.  
    This process includes a number of  steps. I will keep you informed along the way. You can ask me to repeat a step.
    You can also guide me and build on my ideas, with me or separately. You are in the driver’s seat; I am just your tool. 
    """
)

# Create columns for prompts
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Evaluate a sales course"):
        st.session_state["starter_prompt"] = "Evaluate a sales course"
        

with col2:
    if st.button("Assess onboarding material"):
        st.session_state["starter_prompt"] = "Assess onboarding material"


with col3:
    if st.button("Review compliance training"):
        st.session_state["starter_prompt"] = "Review compliance training"

with col4:
    if st.button("Analyze leadership workshop"):
        st.session_state["starter_prompt"] = "Analyze leadership workshop"



# Step 3.1: Confirmation Page
if "uploaded_file" in st.session_state:
    st.header("3.1 Confirmation")
    st.markdown("### File Summary:")
    st.write(f"**Uploaded File Name:** {st.session_state['uploaded_file'].name}")
    st.markdown("#### Follow-Up Questions:")
    st.write("- Did I reasonably capture the intention and goal of your course?")
    st.write("- Are there specific areas of instructional quality you’d like me to focus on?")
    st.write("- Are there any changes you envision to improve the course evaluation?")
    user_feedback = st.text_area("Your feedback (optional):", placeholder="Enter your feedback here...")

st.divider()

# Step 3.2: Level of Expected Critique
if "uploaded_file" in st.session_state:
    st.header("3.2 Level of Expected Critique")
    st.markdown(
        """
        ### Specify the Level of Critique:
        - **0:** Lenient and forgiving; focuses on breadth over depth.
        - **10:** Highly critical; conceptual, philosophical, and detailed.
        """
    )
    critique_level = st.slider("Select your critique level (0-10):", min_value=0, max_value=10, value=5)
    if st.button("Proceed to Evaluation"):
        st.success(f"Critique level set to {critique_level}. Proceeding to evaluation.")
        st.session_state["critique_level"] = critique_level
