def analyze_personality(text):
    traits = []
    if "led" in text or "managed" in text:
        traits.append("Leadership")
    if "collaborated" in text or "team" in text:
        traits.append("Teamwork")
    if "designed" in text or "innovative" in text:
        traits.append("Creativity")
    return traits
