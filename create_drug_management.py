"""
إنشاء جداول الأدوية والمخازن الحقيقية لتتبع الرصيد
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
db = sessionmaker(bind=engine)()

print("إنشاء جداول الأدوية والمخازن...")

# 1. جدول الأدوية الرئيسي
try:
    db.execute(text('''
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_code TEXT UNIQUE NOT NULL,
            trade_name TEXT NOT NULL,
            generic_name TEXT,
            strength TEXT,
            form TEXT,
            manufacturer TEXT,
            unit TEXT,
            reorder_level INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER
        )
    '''))
    print("✓ تم إنشاء جدول drugs")
except Exception as e:
    print(f"⊘ جدول drugs: {e}")

# 2. جدول رصيد الصيدلية (المخزن الرئيسي)
try:
    db.execute(text('''
        CREATE TABLE IF NOT EXISTS pharmacy_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_id INTEGER UNIQUE NOT NULL,
            balance_qty INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (drug_id) REFERENCES drugs(id)
        )
    '''))
    print("✓ تم إنشاء جدول pharmacy_stock (الصيدلية)")
except Exception as e:
    print(f"⊘ جدول pharmacy_stock: {e}")

# 3. جدول رصيد المخزن
try:
    db.execute(text('''
        CREATE TABLE IF NOT EXISTS warehouse_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_id INTEGER UNIQUE NOT NULL,
            balance_qty INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (drug_id) REFERENCES drugs(id)
        )
    '''))
    print("✓ تم إنشاء جدول warehouse_stock (المخزن)")
except Exception as e:
    print(f"⊘ جدول warehouse_stock: {e}")

# 4. جدول حركات الأدوية (تفاصيل كل عملية خصم/إضافة)
try:
    db.execute(text('''
        CREATE TABLE IF NOT EXISTS drug_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_id INTEGER NOT NULL,
            drug_code TEXT,
            transaction_type TEXT NOT NULL,  -- 'pharmacy_to_warehouse', 'warehouse_to_box', 'box_return', 'purchase', 'manual_adjustment'
            quantity_change INTEGER NOT NULL,  -- موجب للإضافة، سالب للخصم
            source TEXT,  -- 'pharmacy', 'warehouse', 'box_id'
            destination TEXT,  -- 'warehouse', 'box_id', etc
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (drug_id) REFERENCES drugs(id)
        )
    '''))
    print("✓ تم إنشاء جدول drug_transactions (حركات الأدوية)")
except Exception as e:
    print(f"⊘ جدول drug_transactions: {e}")

db.commit()
db.close()

print("\n✅ تم إنشاء جداول الأدوية والمخازن بنجاح!")
print("""
الهيكل الجديد:
  drugs           ← بيانات الأدوية الأساسية
  ├─ pharmacy_stock ← رصيد الصيدلية
  ├─ warehouse_stock ← رصيد المخزن
  └─ drug_transactions ← سجل جميع الحركات
""")
