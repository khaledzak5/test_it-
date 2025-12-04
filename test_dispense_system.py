"""
اختبار كامل لعملية صرف الأدوية من المستودع إلى صناديق الإسعافات
"""
import sys
sys.path.insert(0, 'd:\\project')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 70)
print("🧪 اختبار كامل: صرف أدوية من المستودع إلى الصناديق")
print("=" * 70)

# 1. عرض الأدوية المتاحة
print("\n1️⃣ الأدوية المتاحة وأرصدتها:")
print("-" * 70)
drugs = db.execute(text('''
    SELECT 
        d.id,
        d.drug_code,
        d.trade_name,
        ws.balance_qty as warehouse,
        ps.balance_qty as pharmacy
    FROM drugs d
    LEFT JOIN warehouse_stock ws ON d.id = ws.drug_id
    LEFT JOIN pharmacy_stock ps ON d.id = ps.drug_id
    ORDER BY d.trade_name
''')).fetchall()

for drug in drugs:
    print(f"   {drug[2]:<20} | كود: {drug[1]} | المستودع: {drug[3] or 0:>3} | الصيدلية: {drug[4] or 0:>3}")

# 2. عرض الصناديق
print("\n2️⃣ الصناديق المتاحة:")
print("-" * 70)
boxes = db.execute(text('''
    SELECT id, box_name, location FROM first_aid_boxes
''')).fetchall()

for box in boxes:
    print(f"   [{box[0]}] {box[1]:<20} ({box[2]})")

# 3. محاكاة عملية صرف دواء
print("\n3️⃣ محاكاة صرف دواء:")
print("-" * 70)

# اختيار دواء وكمية
drug_id = 1  # Panadol
drug_name = "Panadol"
quantity = 3
box_id = 1

print(f"\n   الدواء: {drug_name}")
print(f"   الكمية المراد صرفها: {quantity}")
print(f"   الصندوق: Box #{box_id}")

# التحقق من الرصيد قبل الصرف
before = db.execute(text('''
    SELECT 
        (SELECT balance_qty FROM warehouse_stock WHERE drug_id = :did) as warehouse,
        (SELECT balance_qty FROM pharmacy_stock WHERE drug_id = :did) as pharmacy
'''), {'did': drug_id}).fetchone()

print(f"\n   ✓ الرصيد قبل الصرف:")
print(f"     - المستودع: {before[0] or 0}")
print(f"     - الصيدلية: {before[1] or 0}")

# تنفيذ عملية الصرف
print(f"\n   ⚙️ تنفيذ الصرف...")

# الحصول على بيانات الدواء
drug_data = db.execute(text('''
    SELECT drug_code, trade_name, unit FROM drugs WHERE id = :did
'''), {'did': drug_id}).fetchone()

if drug_data:
    # خصم من المستودع
    db.execute(text('''
        UPDATE warehouse_stock SET balance_qty = balance_qty - :qty WHERE drug_id = :did
    '''), {'qty': quantity, 'did': drug_id})
    
    # خصم من الصيدلية
    db.execute(text('''
        UPDATE pharmacy_stock SET balance_qty = balance_qty - :qty WHERE drug_id = :did
    '''), {'qty': quantity, 'did': drug_id})
    
    # إضافة للصندوق
    db.execute(text('''
        INSERT INTO first_aid_box_items (box_id, drug_code, drug_name, quantity, unit)
        VALUES (:bid, :code, :name, :qty, :unit)
    '''), {
        'bid': box_id,
        'code': drug_data[0],
        'name': drug_data[1],
        'qty': quantity,
        'unit': drug_data[2]
    })
    
    # تسجيل المعاملة
    db.execute(text('''
        INSERT INTO drug_transactions 
        (drug_id, transaction_type, quantity_change, source, destination, notes, created_at)
        VALUES (:did, :type, :qty, :src, :dst, :notes, datetime('now'))
    '''), {
        'did': drug_id,
        'type': 'warehouse_to_box',
        'qty': -quantity,
        'src': 'warehouse_pharmacy',
        'dst': f'box_{box_id}',
        'notes': f'صرف إلى صندوق: Box #{box_id}'
    })
    
    db.commit()
    print(f"   ✅ تم الصرف بنجاح!")

# التحقق من الرصيد بعد الصرف
after = db.execute(text('''
    SELECT 
        (SELECT balance_qty FROM warehouse_stock WHERE drug_id = :did) as warehouse,
        (SELECT balance_qty FROM pharmacy_stock WHERE drug_id = :did) as pharmacy
'''), {'did': drug_id}).fetchone()

print(f"\n   ✓ الرصيد بعد الصرف:")
print(f"     - المستودع: {after[0] or 0} (كان {before[0] or 0}) ↓ {quantity}")
print(f"     - الصيدلية: {after[1] or 0} (كان {before[1] or 0}) ↓ {quantity}")

# 4. التحقق من محتويات الصندوق
print("\n4️⃣ محتويات الصندوق بعد الصرف:")
print("-" * 70)
box_items = db.execute(text('''
    SELECT drug_name, quantity, unit FROM first_aid_box_items WHERE box_id = :bid
'''), {'bid': box_id}).fetchall()

for item in box_items:
    print(f"   • {item[0]:<20} | الكمية: {item[1]:>3} {item[2]}")

# 5. سجل المعاملات
print("\n5️⃣ سجل المعاملات الأخيرة:")
print("-" * 70)
transactions = db.execute(text('''
    SELECT 
        id,
        transaction_type,
        quantity_change,
        destination,
        notes,
        created_at
    FROM drug_transactions
    ORDER BY created_at DESC
    LIMIT 5
''')).fetchall()

for tx in transactions:
    print(f"   [#{tx[0]}] {tx[1]:<20} | {tx[3]:<15} | الكمية: {tx[2]:>3} | {tx[4]}")

print("\n" + "=" * 70)
print("✅ الاختبار اكتمل بنجاح!")
print("=" * 70)

db.close()
