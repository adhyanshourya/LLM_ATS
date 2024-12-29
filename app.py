from flask import Flask, render_template, request, jsonify
import os
import logging
import PyPDF2 as pdf
import zipfile
import tempfile
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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
            if not text.strip():
                logging.warning(f"No extractable text found in {file_path}")
            return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return None

# Helper function: Extract text from a plain text file
def input_txt_text(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error extracting text from TXT file: {e}")
        return None

# Helper function: Recursively list all supported files in a directory
def list_supported_files(directory, extensions):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(tuple(extensions)):
                files.append(os.path.join(root, filename))
    return files

# Helper function: Get Gemini response
def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error with Gemini API: {e}")
        return None

# Prompt template
input_prompt_template = """
Hey, act like a skilled ATS (Application Tracking System)
with a deep understanding of tech fields like software engineering, data science, data analysis, 
and big data engineering. Evaluate the resume based on the given job description.
Consider the competitive job market and provide assistance for improving resumes.

Primary Skills: {primary_skills}
Secondary Skills: {secondary_skills}

Assign the percentage matching based on the job description with more weightage for primary skills. 
List missing keywords with high accuracy.

Resume: {text}
Job Description: {jd}

I want the response in one single string having the structure:
{{
    "JD Match": "%",
    "MissingKeywords": [],
    "Profile Summary": ""
}}
"""

# Route: Home page
@app.route('/')
def home():
    return render_template('index.html')

# Route: Analyze resumes
@app.route('/analyze', methods=['POST'])
def analyze():
    logging.debug("Analyze route hit")
    job_description = request.form.get('job_description')
    primary_skills = request.form.get('primary_skills', '').split(',')
    secondary_skills = request.form.get('secondary_skills', '').split(',')
    logging.debug(f"Job Description: {job_description}")
    logging.debug(f"Primary Skills: {primary_skills}")
    logging.debug(f"Secondary Skills: {secondary_skills}")

    if 'resume_files' not in request.files:
        logging.debug("No files uploaded")
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist('resume_files')
    logging.debug(f"Number of files uploaded: {len(files)}")

    results = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)

            text = None
            if file.filename.endswith(".pdf"):
                text = input_pdf_text(file_path)
            elif file.filename.endswith(".txt"):
                text = input_txt_text(file_path)
            elif file.filename.endswith(".zip"):
                try:
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                    supported_files = list_supported_files(temp_dir, ['.pdf', '.txt'])
                    for supported_file in supported_files:
                        if supported_file.endswith(".pdf"):
                            text = input_pdf_text(supported_file)
                        elif supported_file.endswith(".txt"):
                            text = input_txt_text(supported_file)
                        if text:
                            prompt = input_prompt_template.format(
                                text=text,
                                jd=job_description,
                                primary_skills=', '.join(primary_skills),
                                secondary_skills=', '.join(secondary_skills)
                            )
                            response = get_gemini_response(prompt)
                            try:
                                result = json.loads(response)
                                result["file_name"] = os.path.basename(supported_file)
                                result["primary_skills"] = primary_skills
                                result["secondary_skills"] = secondary_skills
                                results.append(result)
                            except json.JSONDecodeError as e:
                                logging.error(f"Error parsing Gemini response: {e}")
                                results.append({
                                    "file_name": os.path.basename(supported_file),
                                    "error": "Invalid response from Gemini API"
                                })
                except Exception as e:
                    logging.error(f"Error processing ZIP file: {e}")
                    return jsonify({"error": "Error processing ZIP file"}), 500

    # Sort results by JD Match percentage in descending order
    results = sorted(
        [r for r in results if "JD Match" in r],
        key=lambda x: float(x["JD Match"].strip('%')),
        reverse=True
    )

    logging.debug(f"Sorted analysis results: {results}")
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
