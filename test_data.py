from database import SessionLocal
from models import ReviewHistory, Category, AccessLog
from datetime import datetime

# Get the database session
db = SessionLocal()

# Create sample categories
category1 = Category(name="Electronics", description="Electronic gadgets")
category2 = Category(name="Books", description="Books collection")
category3 = Category(name="Fashion", description="Clothing & accessories")
category4 = Category(name="Home", description="Home appliances")
category5 = Category(name="Beauty", description="Beauty & self-care")

db.add_all([category1, category2, category3, category4, category5])
db.commit()

# Create sample reviews with different versions
review1_v1 = ReviewHistory(text="Good product", stars=8, review_id="R1", category_id=category1.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review1_v2 = ReviewHistory(text="Excellent", stars=9, review_id="R1", category_id=category1.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review1_v3 = ReviewHistory(text="Excellent", stars=10, review_id="R6", category_id=category1.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review1_v4 = ReviewHistory(text="Excellent", stars=10, review_id="R7", category_id=category1.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())


review2_v1 = ReviewHistory(text="Decent book", stars=6, review_id="R2", category_id=category2.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())

review3_v1 = ReviewHistory(text="Nice quality", stars=7, review_id="R3", category_id=category3.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review3_v2 = ReviewHistory(text="Nice quality2", stars=9, review_id="R3", category_id=category3.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())

review4_v1 = ReviewHistory(text="Works well", stars=8, review_id="R4", category_id=category4.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())

review5_v1 = ReviewHistory(text="Amazing1", stars=1, review_id="R5", category_id=category5.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review5_v2 = ReviewHistory(text="Amazing2", stars=3, review_id="R5", category_id=category5.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review5_v3 = ReviewHistory(text="Amazing3", stars=5, review_id="R5", category_id=category5.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review5_v4 = ReviewHistory(text="Amazing4", stars=2, review_id="R5", category_id=category5.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
review5_v5 = ReviewHistory(text="Amazing5", stars=4, review_id="R5", category_id=category5.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())

db.add_all([review1_v1, review1_v2, review2_v1, review3_v1, review3_v2, review4_v1, review5_v1, review5_v2, review5_v3, review5_v4, review5_v5])
db.commit()

# Insert AccessLog entry
log_entry = AccessLog(text="Testing data insertion")
db.add(log_entry)
db.commit()

print("✅ Database seeded successfully!")
db.close()
