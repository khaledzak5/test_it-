"""
اختبار: إضافة دواء لصندوق طوارئ والتحقق من خصم الرصيد
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
db = sessionmaker(bind=engine)()

print("=" * 60)
print("اختبار خصم الرصيد عند إضافة دواء لصندوق طوارئ")
print("=" * 60)

# 1. الحصول على أول دواء
drug = db.execute(text('SELECT id, drug_code, trade_name FROM drugs LIMIT 1')).fetchone()
if not drug:
    print("✗ لا توجد أدوية في قاعدة البيانات!")
    exit(1)

drug_id, drug_code, drug_name = drug
print(f"\n📌 الدواء المختار: {drug_name} (الكود: {drug_code})")

# 2. عرض الرصيد قبل الإضافة
warehouse_before = db.execute(text(
    'SELECT balance_qty FROM warehouse_stock WHERE drug_id = :did'
), {'did': drug_id}).fetchone()

pharmacy_before = db.execute(text(
    'SELECT balance_qty FROM pharmacy_stock WHERE drug_id = :did'
), {'did': drug_id}).fetchone()

warehouse_qty = warehouse_before[0] if warehouse_before else 0
pharmacy_qty = pharmacy_before[0] if pharmacy_before else 0

print(f"\n📊 الرصيد قبل الإضافة:")
print(f"   المخزن (Warehouse): {warehouse_qty} وحدة")
print(f"   الصيدلية (Pharmacy): {pharmacy_qty} وحدة")

# 3. محاكاة إضافة 2 وحدة لصندوق
quantity_to_add = 2
print(f"\n➕ محاكاة: إضافة {quantity_to_add} وحدة لصندوق طوارئ")

db.execute(text('''
    UPDATE warehouse_stock
    SET balance_qty = balance_qty - :qty,
        last_updated = CURRENT_TIMESTAMP
    WHERE drug_id = :did
'''), {'qty': quantity_to_add, 'did': drug_id})

db.execute(text('''
    UPDATE pharmacy_stock
    SET balance_qty = balance_qty - :qty,
        last_updated = CURRENT_TIMESTAMP
    WHERE drug_id = :did
'''), {'qty': quantity_to_add, 'did': drug_id})

db.execute(text('''
    INSERT INTO drug_transactions 
    (drug_id, drug_code, transaction_type, quantity_change, source, destination, notes)
    VALUES (:did, :code, :type, :qty, :src, :dst, :notes)
'''), {
    'did': drug_id,
    'code': drug_code,
    'type': 'warehouse_to_box',
    'qty': -quantity_to_add,
    'src': 'warehouse',
    'dst': 'box_1',
    'notes': 'صندوق طوارئ تجريبي'
})

db.commit()

# 4. عرض الرصيد بعد الإضافة
warehouse_after = db.execute(text(
    'SELECT balance_qty FROM warehouse_stock WHERE drug_id = :did'
), {'did': drug_id}).fetchone()

pharmacy_after = db.execute(text(
    'SELECT balance_qty FROM pharmacy_stock WHERE drug_id = :did'
), {'did': drug_id}).fetchone()

warehouse_qty_after = warehouse_after[0] if warehouse_after else 0
pharmacy_qty_after = pharmacy_after[0] if pharmacy_after else 0

print(f"\n📊 الرصيد بعد الإضافة:")
print(f"   المخزن (Warehouse): {warehouse_qty_after} وحدة (كان {warehouse_qty})")
print(f"   الصيدلية (Pharmacy): {pharmacy_qty_after} وحدة (كان {pharmacy_qty})")

# 5. التحقق من حركة الأدوية
transactions = db.execute(text(
    'SELECT transaction_type, quantity_change, source, destination FROM drug_transactions WHERE drug_id = :did ORDER BY created_at DESC LIMIT 5'
), {'did': drug_id}).fetchall()

print(f"\n📋 آخر 5 حركات للدواء:")
for tx in transactions:
    print(f"   {tx[0]}: {tx[1]:+d} وحدة ({tx[2]} -> {tx[3]})")

# 6. النتيجة النهائية
if warehouse_qty_after == warehouse_qty - quantity_to_add and pharmacy_qty_after == pharmacy_qty - quantity_to_add:
    print(f"\n✅ نجح الاختبار! تم خصم {quantity_to_add} وحدة من كلا الرصيدين بنجاح")
else:
    print(f"\n✗ فشل الاختبار! لم يتم خصم الرصيد بشكل صحيح")

db.close()
