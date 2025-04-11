def detect_bias(text):
    alerts = []
    if "he/she" in text.lower():
        alerts.append("Avoid using gendered language like 'he/she'.")
    if "aggressive" in text.lower():
        alerts.append("Bias alert: Words like 'aggressive' can imply gender bias.")
    return alerts
