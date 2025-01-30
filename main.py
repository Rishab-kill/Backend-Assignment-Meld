from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import models
from database import engine, SessionLocal
from celery_worker import log_access, update_tone_and_sentiment
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CategoryCreate(BaseModel):
    name: str
    description: str

class ReviewCreate(BaseModel):
    text: str
    stars: int
    review_id: str
    category_id: int
    tone: str = None
    sentiment: str = None

@app.get("/reviews/trends")
def get_review_trends(db: Session = Depends(get_db)):
    latest_reviews = (
        db.query(models.ReviewHistory.review_id, func.max(models.ReviewHistory.id).label("latest_id"))
        .group_by(models.ReviewHistory.review_id)
        .subquery()
    )
    print("Latest Reviews ", latest_reviews)

    category_stats = (
        db.query(
            models.Category.id.label("id"),
            models.Category.name.label("name"),
            models.Category.description.label("description"),
            func.avg(models.ReviewHistory.stars).label("average_star"),
            func.count(models.ReviewHistory.id).label("total_review")
        )
        .join(models.ReviewHistory, models.Category.id == models.ReviewHistory.category_id)
        .join(latest_reviews, models.ReviewHistory.id == latest_reviews.c.latest_id)
        .group_by(models.Category.id)
        .order_by(desc("average_star"))
        .limit(5)
        .all()
    )

    print("category_stats ", category_stats)

    result = [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "average_star": round(category.average_star, 2) if category.average_star else 0,
            "total_review": category.total_review
        }
        for category in category_stats
    ]

    log_access.delay("GET /reviews/trends")

    return result

@app.get("/reviews/")
def get_reviews(
        category_id: int,
        cursor: int = Query(None, description="Pagination cursor"),
        db: Session = Depends(get_db)
):
    latest_reviews = (
        db.query(models.ReviewHistory.review_id, func.max(models.ReviewHistory.id).label("latest_id"))
        .group_by(models.ReviewHistory.review_id)
        .subquery()
    )

    query = (
        db.query(
            models.ReviewHistory.id,
            models.ReviewHistory.text,
            models.ReviewHistory.stars,
            models.ReviewHistory.review_id,
            models.ReviewHistory.created_at,
            models.ReviewHistory.tone,
            models.ReviewHistory.sentiment,
            models.ReviewHistory.category_id,
        )
        .join(latest_reviews, models.ReviewHistory.id == latest_reviews.c.latest_id)
        .filter(models.ReviewHistory.category_id == category_id)
        .order_by(desc(models.ReviewHistory.created_at))
    )

    if cursor:
        query = query.filter(models.ReviewHistory.id < cursor)

    reviews = query.limit(15).all()

    for review in reviews:
        if not review.tone or not review.sentiment:
            update_tone_and_sentiment.delay(review.id, review.text, review.stars)


    result = [
        {
            "id": review.id,
            "text": review.text,
            "stars": review.stars,
            "review_id": review.review_id,
            "created_at": review.created_at,
            "tone": review.tone,
            "sentiment": review.sentiment,
            "category_id": review.category_id,
        }
        for review in reviews
    ]

    log_access.delay(f"GET /reviews/?category_id={category_id}")

    return {"reviews": result, "next_cursor": reviews[-1].id if reviews else None}

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

@app.get("/review_history")
def get_review_history(db: Session = Depends(get_db)):
    review_history = db.query(models.ReviewHistory).all()
    return review_history

@app.get("/access_log")
def get_access_log(db: Session = Depends(get_db)):
    access_log = db.query(models.AccessLog).all()
    return access_log


@app.post("/create_categories", response_model=CategoryCreate)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = models.Category(name=category.name, description=category.description)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@app.post("/create_reviews", response_model=ReviewCreate)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == review.category_id).first()
    if not db_category:
        raise HTTPException(status_code=400, detail="Category not found")

    new_review = models.ReviewHistory(
        text=review.text,
        stars=review.stars,
        review_id=review.review_id,
        tone=review.tone,
        sentiment=review.sentiment,
        category_id=review.category_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


