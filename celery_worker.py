from celery import Celery
from database import SessionLocal
import models
import openai

celery = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

openai.api_key = 'OPEN-AI-KEY'

def get_tone_and_sentiment(review_text, stars):
    prompt = f"""
    Review: "{review_text}"
    Rating: {stars} stars

    Please determine the tone of the review (e.g., positive, negative, neutral) and the sentiment (e.g., positive, negative, neutral).
    """

    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )

    analysis = response.choices[0].text.strip()

    tone, sentiment = None, None
    if "Tone:" in analysis and "Sentiment:" in analysis:
        parts = analysis.split("Sentiment:")
        tone = parts[0].replace("Tone:", "").strip()
        sentiment = parts[1].strip() if len(parts) > 1 else None

    return tone, sentiment

@celery.task
def update_tone_and_sentiment(review_id, review_text, stars):
    db = SessionLocal()
    tone, sentiment = get_tone_and_sentiment(review_text, stars)
    db.query(models.ReviewHistory).filter(models.ReviewHistory.id == review_id).update(
        {"tone": tone, "sentiment": sentiment}
    )

    db.commit()
    db.close()

@celery.task
def log_access(access_text: str):
    db = SessionLocal()
    log_entry = models.AccessLog(text=access_text)
    db.add(log_entry)
    db.commit()
    db.close()

