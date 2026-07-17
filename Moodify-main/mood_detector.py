from transformers import pipeline
from keybert import KeyBERT
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ── Load models once at startup ───────────────────────────────
emotion_classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)

kw_model = KeyBERT()
vader = SentimentIntensityAnalyzer()

# ── Emotion to simplified category mapping ────────────────────
EMOTION_CATEGORY = {
    "admiration": "joy", "amusement": "joy", "excitement": "joy",
    "gratitude": "joy", "joy": "joy", "love": "joy",
    "optimism": "joy", "pride": "joy", "relief": "joy",
    "approval": "joy", "caring": "joy",
    "anger": "anger", "annoyance": "anger", "disapproval": "anger",
    "sadness": "sadness", "disappointment": "sadness", "grief": "sadness",
    "remorse": "sadness", "embarrassment": "sadness",
    "fear": "fear", "nervousness": "fear",
    "disgust": "disgust",
    "surprise": "surprise", "confusion": "surprise", "realization": "surprise",
    "curiosity": "surprise",
    "neutral": "neutral", "desire": "neutral",
}


def get_intensity_label(score):
    """Converts confidence score to human readable intensity."""
    if score >= 0.80:
        return "Very High"
    elif score >= 0.60:
        return "High"
    elif score >= 0.40:
        return "Moderate"
    else:
        return "Low"


def detect_mood(text):
    """
    Analyses text and returns:
    - primary_emotion: top detected emotion label
    - primary_category: simplified category for music mapping
    - confidence: confidence score of top emotion
    - intensity: human readable intensity label
    - top_emotions: list of top 3 emotions with percentages
    - keywords: key emotional words extracted from text
    - sentiment: overall polarity from VADER
    """
    try:
        if not text or not text.strip():
            return {
                "primary_emotion": "neutral",
                "primary_category": "neutral",
                "confidence": 0.0,
                "intensity": "Low",
                "top_emotions": [{"label": "neutral", "score": 0.0}],
                "keywords": [],
                "sentiment": "neutral"
            }

        # ── Multi-label emotion detection ─────────────────────
        results = emotion_classifier(text)[0]
        results_sorted = sorted(results, key=lambda x: x['score'], reverse=True)
        top3 = results_sorted[:3]

        primary = top3[0]
        primary_label = primary['label'].lower()
        primary_score = round(primary['score'], 2)
        primary_category = EMOTION_CATEGORY.get(primary_label, "neutral")

        # ── KeyBERT keyword extraction ────────────────────────
        keywords = []
        if len(text.split()) >= 3:
            kw_results = kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=3
            )
            keywords = [kw[0] for kw in kw_results]

        # ── VADER sentiment polarity ──────────────────────────
        vader_scores = vader.polarity_scores(text)
        compound = vader_scores['compound']
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # ── Format top 3 emotions ─────────────────────────────
        top_emotions = [
            {
                "label": e['label'].lower(),
                "score": round(e['score'] * 100, 1)
            }
            for e in top3
        ]

        return {
            "primary_emotion": primary_label,
            "primary_category": primary_category,
            "confidence": primary_score,
            "intensity": get_intensity_label(primary_score),
            "top_emotions": top_emotions,
            "keywords": keywords,
            "sentiment": sentiment
        }

    except Exception as e:
        return {
            "primary_emotion": "neutral",
            "primary_category": "neutral",
            "confidence": 0.0,
            "intensity": "Low",
            "top_emotions": [{"label": "neutral", "score": 0.0}],
            "keywords": [],
            "sentiment": "neutral"
        }
