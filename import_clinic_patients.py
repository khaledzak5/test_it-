"""
سكريبت استيراد جميع بيانات المرضى من ملف Excel إلى قاعدة البيانات
"""

import sqlite3
import pandas as pd
from datetime import datetime

# قراءة ملف Excel
excel_file = 'used_tables_export.xlsx'

try:
    # قراءة جدول clinic_patients من Excel
    df = pd.read_excel(excel_file, sheet_name='clinic_patients')
    print(f"✅ تم قراءة {len(df)} صف من ملف Excel")
    print(f"الأعمدة المتاحة: {list(df.columns)}")
    
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # عد الصفوف الموجودة
    cursor.execute("SELECT COUNT(*) FROM clinic_patients")
    existing_count = cursor.fetchone()[0]
    print(f"\n📊 الصفوف الموجودة في قاعدة البيانات: {existing_count}")
    
    # إدراج البيانات
    inserted = 0
    skipped = 0
    
    for idx, row in df.iterrows():
        try:
            # التحقق من وجود السجل
            trainee_no = str(row.get('trainee_no', '')).strip()
            
            if not trainee_no:
                skipped += 1
                continue
            
            cursor.execute(
                "SELECT COUNT(*) FROM clinic_patients WHERE trainee_no = ?",
                (trainee_no,)
            )
            
            if cursor.fetchone()[0] > 0:
                # تحديث السجل
                cursor.execute("""
                    UPDATE clinic_patients SET
                        full_name = ?,
                        college = ?,
                        department = ?,
                        complaint = ?,
                        diagnosis = ?,
                        record_kind = ?,
                        chronic_json = ?,
                        updated_at = datetime('now')
                    WHERE trainee_no = ?
                """, (
                    str(row.get('full_name', '')),
                    str(row.get('college', '')),
                    str(row.get('department', '')),
                    str(row.get('complaint', '')),
                    str(row.get('diagnosis', '')),
                    str(row.get('record_kind', 'visit')),
                    str(row.get('chronic_json', '{}')),
                    trainee_no
                ))
            else:
                # إدراج سجل جديد
                cursor.execute("""
                    INSERT INTO clinic_patients (
                        trainee_no, full_name, college, department,
                        complaint, diagnosis, record_kind, chronic_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    trainee_no,
                    str(row.get('full_name', '')),
                    str(row.get('college', '')),
                    str(row.get('department', '')),
                    str(row.get('complaint', '')),
                    str(row.get('diagnosis', '')),
                    str(row.get('record_kind', 'visit')),
                    str(row.get('chronic_json', '{}'))
                ))
                inserted += 1
            
            if (idx + 1) % 100 == 0:
                conn.commit()
                print(f"  ✓ تم معالجة {idx + 1} صف...")
        
        except Exception as e:
            print(f"  ❌ خطأ في الصف {idx}: {e}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ اكتمل الاستيراد:")
    print(f"  - تم إدراج: {inserted} سجل جديد")
    print(f"  - تم تحديث: السجلات الموجودة")
    print(f"  - تم تخطي: {skipped} صف")
    print(f"\n📌 إجمالي المرضى في قاعدة البيانات: {existing_count + inserted}")

except Exception as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    import traceback
    traceback.print_exc()
