def detect_fraud(text):
    flags = []
    if "facebook" in text.lower() and "ai" in text.lower():
        flags.append("Exaggerated claim detected: 'built Facebook's AI'.")
    if "google" in text.lower() and "project" not in text.lower():
        flags.append("Claimed Google experience but no project/skills shown.")
    return flags
