# create_hod.py (ضَعْهُ في جذر المشروع)
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

db = SessionLocal()

hod = User(
    full_name="HOD User",
    username="hod1",
    password_hash=hash_password("hod123"),  # غيّرها
    is_admin=False,
    is_hod=True,
    hod_college="كلية نجران",  # 👈 اربطه بكليته
    is_active=True,
)

db.add(hod)
db.commit()
db.close()
print("✅ Created HOD: hod1 / hod123 (كلية نجران)")
