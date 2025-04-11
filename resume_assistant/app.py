from flask import Flask, render_template, request
from utils.resume_parser import parse_resume
from utils.score_calculator import calculate_score, suggest_improvements
from utils.bias_detector import detect_bias
from utils.fraud_checker import detect_fraud
from utils.personality_matcher import analyze_personality

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['resume']
    resume_text = parse_resume(file)

    score, suggestions = calculate_score(resume_text)
    bias_alerts = detect_bias(resume_text)
    fraud_flags = detect_fraud(resume_text)
    soft_skills = analyze_personality(resume_text)

    return render_template('result.html', score=score, suggestions=suggestions,
                           bias=bias_alerts, fraud=fraud_flags, personality=soft_skills)

if __name__ == '__main__':
    app.run(debug=True)
