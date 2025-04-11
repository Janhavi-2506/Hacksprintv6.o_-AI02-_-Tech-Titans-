from flask import Flask, render_template, request, redirect, jsonify
import os
from werkzeug.utils import secure_filename
from utils.parser import extract_text_from_file
from utils.scorer import score_resume, extract_skills

app = Flask(__name__)
UPLOAD_FOLDER = 'resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    resumes = request.files.getlist('resumes')
    job_desc = request.form['job_description']

    results = []
    for resume in resumes:
        filename = secure_filename(resume.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(filepath)

        text = extract_text_from_file(filepath)
        score = score_resume(text, job_desc)
        skills = extract_skills(text)

        results.append({'name': filename, 'score': score, 'skills': skills})

    results.sort(key=lambda x: x['score'], reverse=True)
    return render_template('results.html', results=results, job_desc_skills=extract_skills(job_desc))

if __name__ == '__main__':
    app.run(debug=True)
