from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

username = "admin"
new_password = "admin123"  # غيّرها لاحقًا

user = db.query(User).filter(User.username == username).first()
if not user:
    # إنشاء مستخدم جديد
    user = User(
        full_name="Admin User",
        username=username,
        password_hash=hash_password(new_password),
        is_admin=True,
        is_hod=False,
        is_doc=False,
        hod_college=None,
        is_active=True,
    )
    db.add(user)
    print("✅ تم إنشاء مستخدم admin جديد!")
else:
    # تحديث المستخدم الموجود
    user.password_hash = hash_password(new_password)
    user.is_active = True
    user.is_admin = True  # تأكيد صلاحية الأدمن
    print("✅ تم تحديث كلمة مرور admin!")

db.commit()
db.close()

print(f"📋 بيانات الدخول: {username} / {new_password}")
