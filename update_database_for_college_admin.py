# update_database_for_college_admin.py
# سكربت لإضافة الحقول الجديدة لدعم أدمن الكلية
from app.database import SessionLocal, engine, Base
from app.models import User
from sqlalchemy import text

# إنشاء الجداول إذا لم تكن موجودة
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # التحقق من وجود الأعمدة الجديدة
    from app.database import is_sqlite
    
    if is_sqlite():
        # SQLite - إضافة الأعمدة إذا لم تكن موجودة
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN is_college_admin BOOLEAN DEFAULT 0"))
            print("✅ تم إضافة عمود is_college_admin")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  is_college_admin: {e}")
            else:
                print("ℹ️  عمود is_college_admin موجود بالفعل")
        
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN college_admin_college VARCHAR(255)"))
            print("✅ تم إضافة عمود college_admin_college")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  college_admin_college: {e}")
            else:
                print("ℹ️  عمود college_admin_college موجود بالفعل")
    else:
        # PostgreSQL - إضافة الأعمدة إذا لم تكن موجودة
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_college_admin BOOLEAN DEFAULT FALSE"))
            print("✅ تم إضافة عمود is_college_admin")
        except Exception as e:
            print(f"⚠️  is_college_admin: {e}")
        
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS college_admin_college VARCHAR(255)"))
            print("✅ تم إضافة عمود college_admin_college")
        except Exception as e:
            print(f"⚠️  college_admin_college: {e}")
    
    db.commit()
    print("\n✅ تم تحديث قاعدة البيانات بنجاح!")
    print("📋 يمكنك الآن استخدام ميزة أدمن الكلية")
    
except Exception as e:
    db.rollback()
    print(f"❌ خطأ: {e}")
finally:
    db.close()

