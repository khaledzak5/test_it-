from app.database import SessionLocal, Base, engine
from app.models import Department

Base.metadata.create_all(bind=engine)
db = SessionLocal()
names = ["تقنية المحركات والمركبات", "تقنية القوى الكهربائية", "تقنية ميكانيكا الإنتاج", "تقنية التبريد والتكييف"]
for n in names:
    if not db.query(Department).filter_by(name=n).first():
        db.add(Department(name=n))
db.commit()
db.close()
print("Seeded departments.")
