import pdfplumber
from docx import Document
import re

def parse_resume(filepath):
    text = ""
    
    if filepath.endswith('.pdf'):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
    elif filepath.endswith('.docx'):
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    
    # Basic parsing (you can enhance this with more sophisticated parsing)
    return {
        'raw_text': text,
        'skills': extract_skills(text),
        'experience': extract_experience(text),
        'education': extract_education(text),
        'achievements': extract_achievements(text)
    }

def extract_skills(text):
    # Simple keyword matching - expand this list
    skills = re.findall(r'(python|java|c\+\+|machine learning|ai|flask|django|react)', text, re.IGNORECASE)
    return list(set(skills))

def extract_experience(text):
    # Simple experience extraction
    experience = []
    matches = re.finditer(r'(\b\w+\b\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s+to\s+(present|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})', text, re.IGNORECASE)
    for match in matches:
        experience.append(match.group(0))
    return experience

def extract_education(text):
    # Simple education extraction
    education = []
    edu_keywords = ['university', 'college', 'institute', 'school', 'bachelor', 'master', 'phd']
    sentences = re.split(r'[.!?]', text)
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in edu_keywords):
            education.append(sentence.strip())
    return education

def extract_achievements(text):
    # Extract quantifiable achievements
    achievements = re.findall(r'(increased|reduced|improved|saved)\s+by\s+\d+%', text, re.IGNORECASE)
    return achievements
