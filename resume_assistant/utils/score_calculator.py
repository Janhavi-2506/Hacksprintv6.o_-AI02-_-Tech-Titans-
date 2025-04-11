import re

def calculate_score(text):
    score = 0
    keywords = ["python", "machine learning", "leadership", "team", "project"]
    for kw in keywords:
        if text.lower().count(kw) > 0:
            score += 10

    suggestions = suggest_improvements(text)
    return score, suggestions

def suggest_improvements(text):
    suggestions = []
    if "led" not in text and "managed" not in text:
        suggestions.append("Mention leadership experience like 'led a team of 5'.")
    if re.search(r"increased|reduced|boosted", text, re.IGNORECASE) is None:
        suggestions.append("Add quantifiable achievements, e.g., 'increased sales by 30%'.")
    if text.lower().count("python") < 2:
        suggestions.append("Highlight important skills like 'Python' more frequently.")
    return suggestions
