"""
إنشاء جدول drug_stock_movements لتتبع صرف الأدوية من الصناديق
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
db = sessionmaker(bind=engine)()

# إنشاء جدول drug_stock_movements
print("إنشاء جدول drug_stock_movements...")

try:
    db.execute(text('''
        CREATE TABLE IF NOT EXISTS drug_stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_code TEXT NOT NULL,
            drug_name TEXT,
            movement_type TEXT NOT NULL,  -- 'add_to_box', 'remove_from_box', 'purchase', 'manual_adjustment'
            quantity_change INTEGER NOT NULL,  -- موجب للإضافة، سالب للخصم
            box_id INTEGER,  -- معرف الصندوق (إذا كان الحركة متعلقة بصندوق)
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''))
    db.commit()
    print("✓ تم إنشاء جدول drug_stock_movements")
except Exception as e:
    print(f"⊘ الجدول قد يكون موجود بالفعل: {e}")

# إنشاء جدول drug_balance لتخزين الرصيد الحالي
print("\nإنشاء جدول drug_balance...")

try:
    db.execute(text('''
        CREATE TABLE IF NOT EXISTS drug_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_code TEXT UNIQUE NOT NULL,
            drug_name TEXT,
            current_balance INTEGER DEFAULT 0,  -- الرصيد الحالي
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''))
    db.commit()
    print("✓ تم إنشاء جدول drug_balance")
except Exception as e:
    print(f"⊘ الجدول قد يكون موجود بالفعل: {e}")

db.close()
print("\n✅ تم إنشاء جداول تتبع المخزون بنجاح!")
