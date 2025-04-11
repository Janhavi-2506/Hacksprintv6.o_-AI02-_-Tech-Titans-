from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Example skill keywords (expand this list)
SKILLS = ['python', 'java', 'c++', 'machine learning', 'data analysis', 'excel', 'communication', 'sql', 'html', 'css', 'flask', 'react']

def score_resume(resume_text, job_description):
    docs = [resume_text, job_description]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform(docs)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score * 100, 2)

def extract_skills(text):
    text = text.lower()
    found = []
    for skill in SKILLS:
        if re.search(r'\\b' + re.escape(skill) + r'\\b', text):
            found.append(skill)
    return found
