import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

load_dotenv()  # Load environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Configure API

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

# Streamlit App
st.set_page_config(page_title="GAVS Smart ATS", page_icon=":robot_face:", layout="wide")
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>GAVS Smart ATS</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Upload your resume and paste the job description to get a detailed analysis.</p>",
    unsafe_allow_html=True,
)

# Input Section
col1, col2 = st.columns([1, 1])

with col1:
    jd = st.text_area(
        "Paste the Job Description",
        height=150,
        placeholder="Enter the job description here...",
    )

with col2:
    uploaded_file = st.file_uploader(
        "Upload Your Resume (PDF Only)",
        type="pdf",
        help="Ensure the resume is in PDF format.",
    )

submit = st.button("Analyze Resume")

# Process and Output Section
if submit:
    if not jd:
        st.error("Please provide a job description!")
    elif not uploaded_file:
        st.error("Please upload a resume in PDF format!")
    else:
        with st.spinner("Analyzing resume, please wait..."):
            text = input_pdf_text(uploaded_file)
            prompt = input_prompt.format(text=text, jd=jd)
            response = get_gemini_response(prompt)

            # Parse response (mocked for illustration)
            result = eval(response)  # Replace eval with JSON parsing if needed

            st.success("Analysis Complete!")
            st.markdown("### Results")
            st.write("---")
            st.markdown(
                f"""
                - **Job Description Match:** {result['JD Match']}
                - **Missing Keywords:** {', '.join(result['MissingKeywords'])}
                - **Profile Summary:** {result['Profile Summary']}
                """
            )
# Additional Information Section
st.write("---")
st.markdown(
    "<p style='text-align: center; font-size: 14px;'><strong>Ideation:</strong> Manju Vellaichamy</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 14px;'><strong>Solution and Implementation:</strong> Ajay kr. Mishra</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 14px;'><strong>Reviewed:</strong> Meenakshinathan K</p>",
    unsafe_allow_html=True,
)