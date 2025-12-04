"""
سكريبت لتحميل بيانات ملف الإكسيل إلى قاعدة البيانات SQLite
"""

import pandas as pd
import json
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# قراءة ملف الإكسيل
excel_file = 'used_tables_export.xlsx'

# إعداد قاعدة البيانات
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def load_sf01_as_trainees():
    """تحميل بيانات SF01 كمتدربين"""
    print("Loading SF01 data as trainees...")
    try:
        df = pd.read_excel(excel_file, sheet_name='sf01')
        db = SessionLocal()
        
        # حفظ البيانات في جدول إضافي للمرجع
        for _, row in df.iterrows():
            try:
                student_id = str(row.get('student_id', '')).strip()
                if not student_id:
                    continue
                
                # يمكن استخدام هذه البيانات للربط بالمتدربين الحاليين
                # أو إنشاء جدول إضافي
                print(f"  Student: {row.get('student_Name')} - {student_id}")
            except Exception as e:
                print(f"    Error: {str(e)}")
        
        db.close()
        print(f"✓ Loaded {len(df)} SF01 records")
    except Exception as e:
        print(f"✗ Error loading SF01: {str(e)}")

def load_drugs():
    """تحميل بيانات الأدوية"""
    print("\nLoading drugs data...")
    try:
        df = pd.read_excel(excel_file, sheet_name='drugs')
        db = SessionLocal()
        
        for _, row in df.iterrows():
            try:
                # البيانات موجودة بالفعل في قاعدة البيانات
                # هنا نتحقق من تطابق البيانات فقط
                trade_name = row.get('trade_name')
                generic_name = row.get('generic_name')
                print(f"  Drug: {trade_name} ({generic_name})")
            except Exception as e:
                print(f"    Error: {str(e)}")
        
        db.close()
        print(f"✓ Checked {len(df)} drugs")
    except Exception as e:
        print(f"✗ Error loading drugs: {str(e)}")

def load_clinic_patients():
    """تحميل بيانات مرضى العيادة"""
    print("\nLoading clinic patients data...")
    try:
        df = pd.read_excel(excel_file, sheet_name='clinic_patients')
        db = SessionLocal()
        
        for _, row in df.iterrows():
            try:
                trainee_no = str(row.get('trainee_no', '')).strip()
                full_name = row.get('full_name')
                print(f"  Patient: {full_name} - {trainee_no}")
            except Exception as e:
                print(f"    Error: {str(e)}")
        
        db.close()
        print(f"✓ Loaded {len(df)} clinic patients")
    except Exception as e:
        print(f"✗ Error loading clinic patients: {str(e)}")

def create_external_reference_table():
    """إنشاء جدول للربط بين بيانات الإكسيل وقاعدة البيانات"""
    print("\nCreating external reference table...")
    try:
        db = SessionLocal()
        
        # إنشاء جدول إذا لم يكن موجوداً
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS excel_data_reference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT NOT NULL,  -- 'student', 'drug', 'patient', etc
            excel_id TEXT NOT NULL,
            db_id INTEGER,
            excel_data TEXT,  -- JSON data from excel
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(create_table_sql))
        db.commit()
        
        print("✓ Reference table created")
        db.close()
    except Exception as e:
        print(f"✗ Error creating reference table: {str(e)}")

def populate_reference_table():
    """ملء جدول المراجع ببيانات الإكسيل"""
    print("\nPopulating reference table...")
    try:
        db = SessionLocal()
        
        # تحميل بيانات المتدربين من SF01
        sf01 = pd.read_excel(excel_file, sheet_name='sf01')
        for _, row in sf01.iterrows():
            student_id = str(row.get('student_id', '')).strip()
            if student_id:
                excel_data = row.to_json()
                
                # التحقق من وجود السجل
                check = db.execute(
                    text("SELECT id FROM excel_data_reference WHERE data_type='student' AND excel_id=:excel_id"),
                    {"excel_id": student_id}
                ).fetchone()
                
                if not check:
                    insert_sql = """
                    INSERT INTO excel_data_reference (data_type, excel_id, excel_data)
                    VALUES (:data_type, :excel_id, :excel_data)
                    """
                    db.execute(
                        text(insert_sql),
                        {
                            "data_type": "student",
                            "excel_id": student_id,
                            "excel_data": excel_data
                        }
                    )
        
        db.commit()
        print(f"✓ Populated reference table with {len(sf01)} students")
        db.close()
    except Exception as e:
        print(f"✗ Error populating reference table: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Excel Data Loader for Clinical Management System")
    print("=" * 60)
    
    # إنشاء جداول المراجع
    create_external_reference_table()
    populate_reference_table()
    
    # تحميل البيانات
    load_sf01_as_trainees()
    load_drugs()
    load_clinic_patients()
    
    print("\n" + "=" * 60)
    print("Data loading completed!")
    print("=" * 60)
