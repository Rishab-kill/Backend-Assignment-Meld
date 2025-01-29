from celery import Celery
from database import SessionLocal
import models

celery = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery.task
def log_access(access_text: str):
    db = SessionLocal()
    log_entry = models.AccessLog(text=access_text)
    db.add(log_entry)
    db.commit()
    db.close()
