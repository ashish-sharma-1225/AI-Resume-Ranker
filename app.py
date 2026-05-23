# app.py
import streamlit as st
import pandas as pd
import base64
from resume_ranker.extractor import extract_text_from_pdf
from resume_ranker.preprocess import clean_text
from resume_ranker.ranker import rank_resumes

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Ranker",
    page_icon="🤖",
    layout="centered"
)

# --- Custom CSS for Styling (No Changes Here) ---
def load_css():
    st.markdown("""
    <style>
        /* Your existing CSS from the previous file */
        [data-testid="stAppViewContainer"] { background-color: #001845; }
        [data-testid="stSidebar"] { background-color: #002855; }
        h1 { color: #0466C8; text-align: center; font-weight: bold; }
        h2 { color: #0353A4; border-bottom: 2px solid #0466C8; padding-bottom: 5px; margin-top: 20px; }
        .stMetric { background-color: #002855; border-radius: 10px; padding: 15px; border: 1px solid #0466C8; }
        .stMetric > label { color: #979DAC; font-weight: bold; }
        .stMetric > div > div > p { color: #0466C8; font-size: 2em; }
        div.stButton > button, .stDownloadButton > button { background: linear-gradient(90deg, #0466C8, #0353A4); color: #FFFFFF; border: none; border-radius: 8px; padding: 0.6em 1.2em; font-weight: bold; transition: all 0.2s ease-in-out; }
        div.stButton > button:hover, .stDownloadButton > button:hover { background: linear-gradient(90deg, #0353A4, #023E7D); transform: scale(1.03); }
        .stDataFrame { background-color: #002855 !important; color: #979DAC !important; }
        .stDataFrame thead th { background-color: #0353A4 !important; color: #FFFFFF !important; font-weight: bold; }
        .stDataFrame tbody tr { background-color: #002855; color: #979DAC; }
        .stDataFrame tbody tr:nth-child(even) { background-color: #001233; }
        .stAlert { background-color: #002855 !important; border-left: 4px solid #0466C8 !important; color: #979DAC !important; }
        textarea { background-color: #002855 !important; color: #979DAC !important; border: 1px solid #0466C8 !important; border-radius: 6px !important; }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# Helper function to display PDF from bytes
def display_pdf(file_bytes):
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf" style="border: 1px solid #0466C8;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- Callback and Dialog Functions ---
def handle_row_selection():
    """Callback function to handle row selection in the data_editor."""
    if st.session_state.resume_selector.get("selection", {}).get("rows"):
        selected_row_index = st.session_state.resume_selector["selection"]["rows"][0]
        # Get the dataframe from session state to find the resume name
        df = st.session_state.ranking_df
        if df is not None and not df.empty:
            resume_name = df.iloc[selected_row_index]["Resume Name"]
            # Set the name of the resume to be viewed in the state
            st.session_state.resume_to_view = resume_name
            # Immediately clear the selection to allow re-clicking the same row later
            st.session_state.resume_selector["selection"]["rows"] = []

@st.dialog("View Resume", width="large")
def view_resume_dialog(resume_name):
    """A modal dialog to display the selected PDF."""
    st.markdown(f"### 📄 Viewing: {resume_name}")
    resume_bytes = st.session_state.uploaded_files_bytes.get(resume_name)
    if resume_bytes:
        display_pdf(resume_bytes)
    else:
        st.error("Could not load the resume file.")

# --- Main Application Logic ---
def main():
    load_css()
    # Initialize session state variables
    if "ranking_df" not in st.session_state:
        st.session_state.ranking_df = None
    if "uploaded_files_bytes" not in st.session_state:
        st.session_state.uploaded_files_bytes = {}
    if "resume_to_view" not in st.session_state:
        st.session_state.resume_to_view = None

    with st.sidebar:
        st.header("Setup")
        uploaded_files = st.file_uploader(
            "Upload Resume PDFs", type=["pdf"], accept_multiple_files=True
        )
        job_desc = st.text_area("Paste Job Description", height=200)
        rank_button = st.button("Rank Resumes", use_container_width=True)

    st.title("🤖 AI Resume Ranker")
    st.markdown("---")

    if rank_button:
        if not uploaded_files:
            st.warning("⚠️ Please upload at least one resume.")
        elif not job_desc.strip():
            st.warning("⚠️ Please provide a job description.")
        else:
            with st.spinner("Analyzing and ranking... This may take a moment. ⏳"):
                process_and_rank_resumes(uploaded_files, job_desc)

    # Display results if they exist
    if st.session_state.ranking_df is not None:
        display_results(st.session_state.ranking_df)
    else:
        st.info("👋 Welcome! Please upload resumes and a job description to get started.")

    # Check if a resume has been selected (by the callback) and open the dialog
    if st.session_state.resume_to_view:
        view_resume_dialog(st.session_state.resume_to_view)
        # Reset the state after the dialog is closed by the user
        st.session_state.resume_to_view = None

def process_and_rank_resumes(uploaded_files, job_desc):
    st.session_state.uploaded_files_bytes = {file.name: file.getvalue() for file in uploaded_files}
    file_names = []
    cleaned_resumes = []
    for uploaded_file in uploaded_files:
        raw_text = extract_text_from_pdf(uploaded_file.getvalue())
        cleaned_text = clean_text(raw_text)
        file_names.append(uploaded_file.name)
        cleaned_resumes.append(cleaned_text)

    cleaned_jd = clean_text(job_desc)
    ranking = rank_resumes(cleaned_resumes, cleaned_jd)

    results = []
    for rank_info in ranking:
        idx = rank_info['index']
        score = rank_info['score'] * 100
        results.append({
            "Rank": len(results) + 1,
            "Resume Name": file_names[idx],
            "Match Score (%)": f"{score:.2f}"
        })
    st.session_state.ranking_df = pd.DataFrame(results)

def display_results(df):
    st.success("✅ Ranking complete!")
    st.header("🏆 Top 3 Candidates")
    top_3_resumes = df.head(3)

    cols = st.columns(len(top_3_resumes) if len(top_3_resumes) > 0 else 1)
    for i, col in enumerate(cols):
        if i < len(top_3_resumes):
            with col:
                st.metric(
                    label=f"📄 {top_3_resumes.iloc[i]['Resume Name']}",
                    value=f"{top_3_resumes.iloc[i]['Match Score (%)']}%",
                    delta=f"Rank #{top_3_resumes.iloc[i]['Rank']}",
                    delta_color="off"
                )
    st.markdown("---")

    st.header("📊 Full Ranking Details")
    st.info("Click on any row in the table below to view the resume.")

    st.data_editor(
        df,
        key="resume_selector",
        hide_index=True,
        use_container_width=True,
        disabled=("Rank", "Resume Name", "Match Score (%)"),
        on_change=handle_row_selection # Set the callback function here
    )

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv,
        file_name="resume_ranking.csv",
        mime="text/csv",
        use_container_width=True
    )

if __name__ == "__main__":
    main()