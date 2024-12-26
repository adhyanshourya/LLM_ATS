import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import zipfile
import tempfile
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Helper function: Extract text from a PDF file
def input_pdf_text(file_path):
    try:
        with open(file_path, "rb") as f:
            reader = pdf.PdfReader(f)
            text = ""
            for page in range(len(reader.pages)):
                page_content = reader.pages[page].extract_text()
                if page_content:
                    text += page_content
            return text
    except Exception as e:
        return None

# Helper function: Extract relevant experience
def extract_relevant_experience(resume_text, job_description):
    # Mock implementation: Customize as needed
    years_of_experience = 5  # Example extracted value
    return f"{years_of_experience} years (extracted based on resume and JD analysis)"

# Helper function: Analyze job change frequency
def analyze_job_change_frequency(resume_text):
    # Mock implementation: Customize as needed
    frequency = 3  # Example extracted value
    return f"{frequency} job changes detected in the resume"

# Helper function: Perform sentiment analysis
def perform_sentiment_analysis(resume_text):
    # Mock implementation: Customize as needed
    sentiment = "Positive"  # Example sentiment
    return f"Overall sentiment of the resume is {sentiment}"

# Helper function: Skill gap analysis
def skill_gap_analysis(resume_text, job_description):
    # Mock implementation: Customize as needed
    gaps = ["AWS", "Kubernetes"]  # Example gaps
    return f"Skill gaps identified: {', '.join(gaps)}"

# Helper function: Get Gemini response
def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Helper function: Recursively list all PDF files in a directory
def list_pdf_files(directory):
    pdf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

# Prompt template
input_prompt_template = """
Hey, act like a skilled ATS (Application Tracking System)
with a deep understanding of tech fields like software engineering, data science, data analysis, 
and big data engineering. Evaluate the resume based on the given job description.
Consider the competitive job market and provide assistance for improving resumes.

Assign the percentage matching based on the job description and 
list missing keywords with high accuracy.

Resume: {text}
Job Description: {jd}

I want the response in one single string having the structure:
{{
    "JD Match": "%",
    "MissingKeywords": [],
    "Profile Summary": ""
}}
"""

# Streamlit app setup
st.title("✨ GAVS Smart ATS ")
st.markdown("Evaluate resumes individually or in bulk!")

# Job description input
st.header("📝 Job Description")
jd = st.text_area("Paste the Job Description", height=150, placeholder="Enter the job description here...")

# File upload
st.header("📂 Upload Resumes")
uploaded_file = st.file_uploader(
    "Upload a single PDF or ZIP file containing resumes",
    type=["pdf", "zip"],
    help="Accepted formats: .pdf (single resume) or .zip (multiple resumes in PDF format)"
)

# Submit button
if st.button("Analyze"):
    if not jd:
        st.error("❗ Please provide a job description for evaluation.")
    elif uploaded_file is None:
        st.error("❗ Please upload a PDF or ZIP file.")
    else:
        if uploaded_file.name.endswith(".pdf"):
            # Process single PDF file
            st.info("📄 Processing single resume...")
            text = input_pdf_text(uploaded_file)
            if text:
                prompt = input_prompt_template.format(text=text, jd=jd)
                response = get_gemini_response(prompt)

                # Additional analyses
                relevant_experience = extract_relevant_experience(text, jd)
                job_change_frequency = analyze_job_change_frequency(text)
                sentiment_analysis = perform_sentiment_analysis(text)
                skill_gaps = skill_gap_analysis(text, jd)

                # Parse response
                result = json.loads(response)

                st.success("✅ Analysis Completed!")
                st.markdown("### Results")
                st.write("---")

                with st.expander("Job Description Match Analysis"):
                    st.markdown(f"**Job Description Match:** {result['JD Match']}")

                with st.expander("Missing Keywords Analysis"):
                    st.markdown(f"**Missing Keywords:** {', '.join(result['MissingKeywords'])}")

                with st.expander("Profile Summary Analysis"):
                    st.markdown(f"**Profile Summary:** {result['Profile Summary']}")

                with st.expander("Relevant Experience Analysis"):
                    st.markdown(f"**Relevant Experience:** {relevant_experience}")

                with st.expander("Job Change Frequency Analysis"):
                    st.markdown(f"**Job Change Frequency:** {job_change_frequency}")

                with st.expander("Sentiment Analysis"):
                    st.markdown(f"**Sentiment Analysis:** {sentiment_analysis}")

                with st.expander("Skill Gap Analysis"):
                    st.markdown(f"**Skill Gaps:** {skill_gaps}")
            else:
                st.error("❗ Unable to extract text from the uploaded PDF. Ensure it is a searchable PDF.")
        elif uploaded_file.name.endswith(".zip"):
            # Process ZIP file with multiple resumes
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)

                    # Recursively list all PDF files in extracted content
                    pdf_files = list_pdf_files(temp_dir)

                    if not pdf_files:
                        st.error("❗ No PDF files found in the uploaded ZIP folder. Ensure the files have valid '.pdf' extensions.")
                    elif len(pdf_files) > 200:
                        st.error("❗ ZIP folder contains more than the allowed maximum of 200 resumes.")
                    else:
                        st.info(f"📄 Processing {len(pdf_files)} resumes...")
                        results = []
                        for pdf_file in pdf_files:
                            text = input_pdf_text(pdf_file)
                            if text:
                                prompt = input_prompt_template.format(text=text, jd=jd)
                                response = get_gemini_response(prompt)

                                # Additional analyses
                                relevant_experience = extract_relevant_experience(text, jd)
                                job_change_frequency = analyze_job_change_frequency(text)
                                sentiment_analysis = perform_sentiment_analysis(text)
                                skill_gaps = skill_gap_analysis(text, jd)

                                # Parse response
                                result = json.loads(response)
                                results.append({
                                    "file_name": os.path.basename(pdf_file),
                                    "response": result,
                                    "relevant_experience": relevant_experience,
                                    "job_change_frequency": job_change_frequency,
                                    "sentiment_analysis": sentiment_analysis,
                                    "skill_gaps": skill_gaps
                                })

                        # Display Results
                        if results:
                            st.success("✅ Analysis completed. See results below:")
                            for result in results:
                                with st.expander(f"📄 {result['file_name']}"):
                                    st.json(result)
                        else:
                            st.error("❗ No valid resumes found in the ZIP folder. Ensure they are searchable PDFs.")
                except Exception as e:
                    st.error(f"❗ Error processing ZIP file: {e}")
