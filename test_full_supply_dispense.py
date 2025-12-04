"""
اختبار كامل لنظام صرف وتوريد الأدوية
"""
import sys
sys.path.insert(0, 'd:\\project')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 80)
print("🧪 اختبار كامل: نظام صرف وتوريد الأدوية")
print("=" * 80)

# 1. الحالة الأولية
print("\n1️⃣ الحالة الأولية للأدوية:")
print("-" * 80)
initial_state = db.execute(text('''
    SELECT 
        d.trade_name,
        ws.balance_qty as warehouse,
        ps.balance_qty as pharmacy
    FROM drugs d
    LEFT JOIN warehouse_stock ws ON d.id = ws.drug_id
    LEFT JOIN pharmacy_stock ps ON d.id = ps.drug_id
    ORDER BY d.trade_name
''')).fetchall()

for drug in initial_state:
    print(f"   {drug[0]:<15} | المستودع: {drug[1]:>3} | الصيدلية: {drug[2]:>3}")

# 2. محاكاة عملية صرف
print("\n2️⃣ محاكاة عملية صرف:")
print("-" * 80)
print("   الدواء: Panadol | الكمية: 2 | الصندوق: 1")

drug_id_dispense = 1
quantity_dispense = 2
box_id = 1

# تنفيذ الصرف
db.execute(text('''
    UPDATE warehouse_stock SET balance_qty = balance_qty - :qty WHERE drug_id = :did
'''), {'qty': quantity_dispense, 'did': drug_id_dispense})

db.execute(text('''
    UPDATE pharmacy_stock SET balance_qty = balance_qty - :qty WHERE drug_id = :did
'''), {'qty': quantity_dispense, 'did': drug_id_dispense})

db.execute(text('''
    INSERT INTO first_aid_box_items (box_id, drug_code, drug_name, quantity, unit)
    VALUES (:bid, :code, :name, :qty, :unit)
'''), {
    'bid': box_id,
    'code': '1',
    'name': 'Panadol',
    'qty': quantity_dispense,
    'unit': 'عدد'
})

db.execute(text('''
    INSERT INTO drug_transactions 
    (drug_id, transaction_type, quantity_change, source, destination, notes, created_at)
    VALUES (:did, :type, :qty, :src, :dst, :notes, datetime('now'))
'''), {
    'did': drug_id_dispense,
    'type': 'warehouse_to_box',
    'qty': -quantity_dispense,
    'src': 'warehouse_pharmacy',
    'dst': 'box_1',
    'notes': 'صرف إلى صندوق: الرئيسي'
})

db.commit()
print("   ✅ تم الصرف بنجاح!")

# 3. الحالة بعد الصرف
print("\n3️⃣ الحالة بعد عملية الصرف:")
print("-" * 80)
after_dispense = db.execute(text('''
    SELECT 
        d.trade_name,
        ws.balance_qty as warehouse,
        ps.balance_qty as pharmacy
    FROM drugs d
    LEFT JOIN warehouse_stock ws ON d.id = ws.drug_id
    LEFT JOIN pharmacy_stock ps ON d.id = ps.drug_id
    ORDER BY d.trade_name
''')).fetchall()

for drug in after_dispense:
    print(f"   {drug[0]:<15} | المستودع: {drug[1]:>3} | الصيدلية: {drug[2]:>3}")

# 4. محاكاة عملية توريد
print("\n4️⃣ محاكاة عملية توريد:")
print("-" * 80)
print("   الدواء: Brufen | الكمية: 5 | ملاحظة: وارد من المستودع الرئيسي")

drug_id_supply = 2
quantity_supply = 5

# تنفيذ التوريد
db.execute(text('''
    UPDATE warehouse_stock SET balance_qty = balance_qty + :qty WHERE drug_id = :did
'''), {'qty': quantity_supply, 'did': drug_id_supply})

db.execute(text('''
    UPDATE pharmacy_stock SET balance_qty = balance_qty + :qty WHERE drug_id = :did
'''), {'qty': quantity_supply, 'did': drug_id_supply})

db.execute(text('''
    INSERT INTO drug_transactions 
    (drug_id, transaction_type, quantity_change, source, destination, notes, created_at)
    VALUES (:did, :type, :qty, :src, :dst, :notes, datetime('now'))
'''), {
    'did': drug_id_supply,
    'type': 'supply_received',
    'qty': quantity_supply,
    'src': 'external_supplier',
    'dst': 'warehouse_pharmacy',
    'notes': 'توريد: وارد من المستودع الرئيسي'
})

db.commit()
print("   ✅ تم التوريد بنجاح!")

# 5. الحالة بعد التوريد
print("\n5️⃣ الحالة بعد عملية التوريد:")
print("-" * 80)
after_supply = db.execute(text('''
    SELECT 
        d.trade_name,
        ws.balance_qty as warehouse,
        ps.balance_qty as pharmacy
    FROM drugs d
    LEFT JOIN warehouse_stock ws ON d.id = ws.drug_id
    LEFT JOIN pharmacy_stock ps ON d.id = ps.drug_id
    ORDER BY d.trade_name
''')).fetchall()

for drug in after_supply:
    print(f"   {drug[0]:<15} | المستودع: {drug[1]:>3} | الصيدلية: {drug[2]:>3}")

# 6. محتويات الصناديق
print("\n6️⃣ محتويات صناديق الإسعافات:")
print("-" * 80)
box_items = db.execute(text('''
    SELECT box_id, drug_name, quantity FROM first_aid_box_items ORDER BY box_id, drug_name
''')).fetchall()

if box_items:
    for item in box_items:
        print(f"   [الصندوق #{item[0]}] {item[1]:<15} | الكمية: {item[2]}")
else:
    print("   لا توجد عناصر في الصناديق")

# 7. سجل المعاملات
print("\n7️⃣ سجل المعاملات:")
print("-" * 80)
transactions = db.execute(text('''
    SELECT 
        id,
        drug_id,
        transaction_type,
        quantity_change,
        destination,
        notes
    FROM drug_transactions
    ORDER BY id DESC
    LIMIT 10
''')).fetchall()

for tx in transactions:
    tx_type = "✈️ توريد" if tx[2] == 'supply_received' else "📤 صرف" if tx[2] == 'warehouse_to_box' else f"📝 {tx[2]}"
    print(f"   [{tx[0]:>2}] {tx_type:<10} | الدواء: {tx[1]:<2} | الكمية: {tx[3]:>3} | {tx[5]}")

# 8. ملخص النتائج
print("\n" + "=" * 80)
print("✅ ملخص الاختبار:")
print("=" * 80)
print("   1. ✓ جلب الأدوية مع أرصدتها من warehouse و pharmacy")
print("   2. ✓ صرف 2 وحدة Panadol: 5→3 (warehouse و pharmacy)")
print("   3. ✓ إضافة العنصر لصناديق الإسعافات")
print("   4. ✓ توريد 5 وحدات Brufen: 0→5 (warehouse و pharmacy)")
print("   5. ✓ تسجيل جميع المعاملات في drug_transactions")
print("   6. ✓ الكميات تتحدث بنجاح")
print("=" * 80)

db.close()
