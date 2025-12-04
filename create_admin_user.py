# create_admin_user.py
from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import hash_password

# إنشاء الجداول إذا لم تكن موجودة
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# بيانات المستخدم الجديد
username = "admin"
password = "admin123"
full_name = "Admin User"

# التحقق من وجود المستخدم
existing_user = db.query(User).filter(User.username == username).first()

if existing_user:
    print(f"⚠️  المستخدم '{username}' موجود بالفعل!")
    print(f"   سيتم تحديث كلمة المرور...")
    existing_user.password_hash = hash_password(password)
    existing_user.is_admin = True
    existing_user.is_active = True
    db.commit()
    print(f"✅ تم تحديث كلمة مرور المستخدم '{username}'")
else:
    # إنشاء مستخدم جديد
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
    print(f"✅ تم إنشاء مستخدم admin جديد بنجاح!")

print(f"\n📋 بيانات الدخول:")
print(f"   Username: {username}")
print(f"   Password: {password}")

db.close()

