# create_admin.py (جذر المشروع)
from passlib.hash import bcrypt
from app.database import SessionLocal, engine, Base
from app.models import User

Base.metadata.create_all(bind=engine)
db = SessionLocal()

password_plain = "admin123"
hashed = bcrypt.hash(password_plain)

admin = User(
    full_name="Admin User",
    username="admin",
    password_hash=hashed,  # تأكد أن عمودك اسمه password_hash
    is_admin=True,
    is_hod=False,
    hod_college=None,
    is_active=True,
)

db.add(admin)
db.commit()
db.close()

print("✅ Created admin: admin / admin123")
