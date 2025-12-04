"""
تحميل الأدوية من Excel إلى جداول الأدوية والمخازن
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
db = sessionmaker(bind=engine)()

print("تحميل الأدوية من Excel...")

try:
    import sys
    import os
    sys.path.insert(0, os.getcwd())
    from excel_data_reference import get_all_drugs
    
    drugs = get_all_drugs()
    print(f"وجدت {len(drugs)} دواء في Excel")
    
    count_inserted = 0
    for drug in drugs:
        try:
            drug_code = str(drug.get('id', '')).strip()
            trade_name = drug.get('trade_name', '')
            generic_name = drug.get('generic_name', '')
            strength = drug.get('strength', '')
            form = drug.get('form', '')
            unit = drug.get('unit', '')
            stock_qty = int(drug.get('stock_qty', 0)) if drug.get('stock_qty') else 0
            reorder_level = int(drug.get('reorder_level', 0)) if drug.get('reorder_level') else 0
            
            if not drug_code or not trade_name:
                continue
            
            # تحقق من وجود الدواء
            existing = db.execute(text(
                'SELECT id FROM drugs WHERE drug_code = :code'
            ), {'code': drug_code}).fetchone()
            
            if existing:
                # تحديث الدواء الموجود
                db.execute(text('''
                    UPDATE drugs
                    SET trade_name = :name, generic_name = :gen, strength = :str,
                        form = :form, unit = :unit, reorder_level = :level
                    WHERE drug_code = :code
                '''), {
                    'name': trade_name, 'gen': generic_name, 'str': strength,
                    'form': form, 'unit': unit, 'level': reorder_level,
                    'code': drug_code
                })
                drug_id = existing[0]
            else:
                # إدراج دواء جديد
                db.execute(text('''
                    INSERT INTO drugs (drug_code, trade_name, generic_name, strength, form, unit, reorder_level)
                    VALUES (:code, :name, :gen, :str, :form, :unit, :level)
                '''), {
                    'code': drug_code, 'name': trade_name, 'gen': generic_name,
                    'str': strength, 'form': form, 'unit': unit, 'level': reorder_level
                })
                db.commit()
                drug_id = db.execute(text(
                    'SELECT id FROM drugs WHERE drug_code = :code'
                ), {'code': drug_code}).fetchone()[0]
                count_inserted += 1
            
            # تحديث رصيد الصيدلية
            existing_pharmacy = db.execute(text(
                'SELECT id FROM pharmacy_stock WHERE drug_id = :did'
            ), {'did': drug_id}).fetchone()
            
            if existing_pharmacy:
                db.execute(text(
                    'UPDATE pharmacy_stock SET balance_qty = :qty WHERE drug_id = :did'
                ), {'qty': stock_qty, 'did': drug_id})
            else:
                db.execute(text(
                    'INSERT INTO pharmacy_stock (drug_id, balance_qty) VALUES (:did, :qty)'
                ), {'did': drug_id, 'qty': stock_qty})
            
            # تحديث رصيد المخزن (ابدأ برصيد الصيدلية)
            existing_warehouse = db.execute(text(
                'SELECT id FROM warehouse_stock WHERE drug_id = :did'
            ), {'did': drug_id}).fetchone()
            
            if not existing_warehouse:
                db.execute(text(
                    'INSERT INTO warehouse_stock (drug_id, balance_qty) VALUES (:did, :qty)'
                ), {'did': drug_id, 'qty': stock_qty})
            
        except Exception as e:
            print(f"  ⊘ خطأ في {drug.get('trade_name', 'unknown')}: {e}")
            continue
    
    db.commit()
    print(f"✓ تم تحميل {count_inserted} دواء جديد")
    
    # عرض إحصائيات
    total = db.execute(text('SELECT COUNT(*) FROM drugs')).scalar()
    pharmacy_balance = db.execute(text('SELECT SUM(balance_qty) FROM pharmacy_stock')).scalar() or 0
    warehouse_balance = db.execute(text('SELECT SUM(balance_qty) FROM warehouse_stock')).scalar() or 0
    
    print(f"\n📊 الإحصائيات:")
    print(f"  إجمالي الأدوية: {total}")
    print(f"  رصيد الصيدلية: {pharmacy_balance} وحدة")
    print(f"  رصيد المخزن: {warehouse_balance} وحدة")
    
except Exception as e:
    print(f"✗ خطأ: {e}")
finally:
    db.close()

print("\n✅ تم تحديث الأدوية بنجاح!")
