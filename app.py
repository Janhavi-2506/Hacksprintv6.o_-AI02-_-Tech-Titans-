from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from utils.resume_parser import parse_resume
from utils.ai_analyzer import analyze_resume, detect_bias, detect_fraud, analyze_personality

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return redirect(request.url)
    
    file = request.files['resume']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse and analyze resume
        resume_data = parse_resume(filepath)
        analysis = analyze_resume(resume_data, request.form.get('job_description', ''))
        
        # Add additional analyses
        analysis['bias_detection'] = detect_bias(resume_data)
        analysis['fraud_detection'] = detect_fraud(resume_data)
        analysis['personality'] = analyze_personality(resume_data)
        
        return render_template('results.html', analysis=analysis, resume_data=resume_data)
    
    return redirect(request.url)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
