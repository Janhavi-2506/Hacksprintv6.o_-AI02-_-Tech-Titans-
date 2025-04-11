from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def analyze_resume(resume_data, job_description=""):
    # Calculate resume health score
    health_score = calculate_health_score(resume_data)
    
    # Calculate match score if job description is provided
    match_score = 0
    improvement_suggestions = []
    
    if job_description:
        # Simple TF-IDF based matching
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([resume_data['raw_text'], job_description])
        match_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
        
        # Generate improvement suggestions
        required_skills = extract_skills(job_description)
        missing_skills = [skill for skill in required_skills if skill.lower() not in [s.lower() for s in resume_data['skills']]
        
        if missing_skills:
            improvement_suggestions.append(f"The job requires these skills that are missing from your resume: {', '.join(missing_skills)}")
        
        if not resume_data['achievements']:
            improvement_suggestions.append("Your resume lacks quantifiable achievements. Add metrics like 'increased sales by 30%'.")
    
    return {
        'health_score': health_score,
        'match_score': match_score,
        'improvement_suggestions': improvement_suggestions
    }

def calculate_health_score(resume_data):
    score = 50  # Base score
    
    # Add points for good elements
    if len(resume_data['skills']) >= 5:
        score += 10
    if len(resume_data['experience']) >= 1:
        score += 15
    if len(resume_data['education']) >= 1:
        score += 10
    if len(resume_data['achievements']) >= 1:
        score += 15
    
    # Deduct points for issues
    if len(resume_data['raw_text']) > 1000:  # Too long
        score -= 5
    if len(resume_data['raw_text']) < 200:   # Too short
        score -= 10
    
    return min(max(score, 0), 100)  # Ensure score is between 0-100

def detect_bias(resume_data):
    # Check for gendered language in resume
    gendered_words = ['he', 'she', 'him', 'her', 'his', 'hers']
    found_bias = []
    
    for word in gendered_words:
        if re.search(r'\b' + word + r'\b', resume_data['raw_text'], re.IGNORECASE):
            found_bias.append(f"Potential gendered language: '{word}'")
    
    return {
        'bias_found': len(found_bias) > 0,
        'bias_messages': found_bias
    }

def detect_fraud(resume_data):
    # Simple fraud detection
    red_flags = []
    
    # Check for exaggerated claims
    exaggerated_phrases = ['built facebook', 'created google', 'invented']
    for phrase in exaggerated_phrases:
        if phrase in resume_data['raw_text'].lower():
            red_flags.append(f"Potential exaggeration: '{phrase}'")
    
    # Check for experience without supporting skills
    if len(resume_data['experience']) > 2 and len(resume_data['skills']) < 3:
        red_flags.append("Multiple positions listed but few skills mentioned")
    
    return {
        'fraud_risk': len(red_flags) > 0,
        'fraud_messages': red_flags,
        'fraud_score': min(len(red_flags) * 20, 100)  # 20 points per red flag
    }

def analyze_personality(resume_data):
    # Personality trait analysis
    traits = {
        'leadership': 0,
        'teamwork': 0,
        'creativity': 0
    }
    
    text = resume_data['raw_text'].lower()
    
    # Leadership indicators
    leadership_phrases = ['led', 'managed', 'directed', 'supervised']
    for phrase in leadership_phrases:
        traits['leadership'] += text.count(phrase)
    
    # Teamwork indicators
    teamwork_phrases = ['team', 'collaborat', 'worked with', 'coordinate']
    for phrase in teamwork_phrases:
        traits['teamwork'] += text.count(phrase)
    
    # Creativity indicators
    creativity_phrases = ['created', 'designed', 'innovative', 'developed']
    for phrase in creativity_phrases:
        traits['creativity'] += text.count(phrase)
    
    # Normalize scores (0-100)
    max_count = max(traits.values()) or 1
    for trait in traits:
        traits[trait] = int((traits[trait] / max_count) * 100)
    
    return traits
