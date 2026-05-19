from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1
)

def detect_mood(text):
    """
    Takes a string of text and returns the detected emotion
    and its confidence score. Returns neutral on failure.
    """
    try:
        if not text or not text.strip():
            return "neutral", 0.0

        result = emotion_classifier(text)
        emotion = result[0][0]['label'].lower()
        score = round(result[0][0]['score'], 2)
        return emotion, score

    except Exception:
        return "neutral", 0.0