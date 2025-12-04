# create_admin.py
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

db = SessionLocal()
admin = User(
    full_name="Admin User",
    username="admin",
    password_hash=hash_password("admin123"),  # غيّرها
    is_admin=True,
    is_hod=False,
    hod_college=None
)
db.add(admin)
db.commit()
db.close()
print("✅ Created admin: admin/admin123")
