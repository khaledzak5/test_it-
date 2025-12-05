"""
إضافة عمود manufacturer وتحديث أعمدة أخرى في جدول drugs
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
db = sessionmaker(bind=engine)()

print("🔄 تحديث جدول drugs...")

try:
    # التحقق من وجود الأعمدة وإضافتها إن لم تكن موجودة
    columns_to_add = [
        ("manufacturer", "TEXT"),
        ("created_by", "INTEGER"),
        ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("updated_by", "INTEGER"),
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            # محاولة إضافة العمود
            db.execute(text(f"""
                ALTER TABLE drugs ADD COLUMN {col_name} {col_type}
            """))
            print(f"✓ تم إضافة عمود {col_name}")
        except Exception as e:
            if "duplicate column" in str(e) or "already exists" in str(e):
                print(f"⊘ عمود {col_name} موجود بالفعل")
            else:
                print(f"⚠ خطأ في إضافة {col_name}: {e}")
    
    db.commit()
    print("\n✅ تم تحديث جدول drugs بنجاح!")
    
except Exception as e:
    print(f"❌ خطأ: {e}")
    db.rollback()
finally:
    db.close()
