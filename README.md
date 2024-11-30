# LLM_ATS
ATS Score: Resume Matcher
Overview
The ATS Score: Resume Matcher is a tool designed to evaluate how well a resume aligns with a job description. By leveraging the Google Gemini API, the project analyzes both the resume and the job description, providing a compatibility score (in %) along with detailed insights into the match.

Features
PDF Parsing: Automatically reads resumes and job descriptions in PDF format and converts them to text.
Match Analysis: Provides a percentage score indicating the match between the resume and the job description.
Detailed Feedback: Offers a description of key matches and areas of improvement.
User-Friendly Output: Clear, concise, and actionable results to help job seekers and recruiters.
Technologies Used
Python: Core programming language for processing.
Google Gemini API: Used to extract text from PDFs and perform advanced text analysis.
Flask/Streamlit (optional): For creating a user-friendly interface.
How It Works
Input PDFs: Users upload a resume and a job description in PDF format.
Text Extraction: The tool uses the Google Gemini API to extract text from the uploaded PDFs.
Text Analysis: The extracted text is analyzed to calculate a compatibility score.
Results: A percentage score and detailed insights are provided to the user.
Setup Instructions
Prerequisites
Python 3.8 or above
Google Gemini API key (sign up at Google Cloud to obtain your API key)