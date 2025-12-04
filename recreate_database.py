# recreate_database.py
from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import hash_password

# حذف جميع الجداول القديمة وإنشاء جديدة
print("🔄 إعادة إنشاء قاعدة البيانات...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ تم إنشاء قاعدة البيانات بنجاح!")

# إنشاء مستخدم admin
db = SessionLocal()

username = "admin"
password = "admin123"
full_name = "Admin User"

new_admin = User(
    full_name=full_name,
    username=username,
    password_hash=hash_password(password),
    is_admin=True,
    is_hod=False,
    is_doc=False,
    hod_college=None,
    is_active=True,
)

db.add(new_admin)
db.commit()
db.close()

print(f"✅ تم إنشاء مستخدم admin!")
print(f"\n📋 بيانات الدخول:")
print(f"   Username: {username}")
print(f"   Password: {password}")

