"""
سكريبت لإنشاء جدول clinic_patients وتحميل البيانات من الإكسيل
"""

import pandas as pd
import sys
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# إعداد قاعدة البيانات
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def create_clinic_patients_table():
    """إنشاء جدول clinic_patients"""
    print("Creating clinic_patients table...")
    try:
        db = SessionLocal()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS clinic_patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_kind TEXT NOT NULL DEFAULT 'patient',
            patient_type TEXT,
            trainee_no TEXT UNIQUE,
            full_name TEXT,
            national_id TEXT,
            mobile TEXT,
            major TEXT,
            college TEXT,
            birth_date TEXT,
            department TEXT,
            gender TEXT,
            address TEXT,
            email TEXT,
            visit_date TEXT,
            visit_reason TEXT,
            diagnosis TEXT,
            treatment TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(create_table_sql))
        db.commit()
        
        print("✓ Table created successfully")
        db.close()
        return True
    except Exception as e:
        print(f"✗ Error creating table: {str(e)}")
        return False

def load_clinic_patients_from_excel():
    """تحميل بيانات مرضى العيادة من الإكسيل"""
    print("\nLoading clinic patients data from Excel...")
    try:
        # قراءة ملف الإكسيل
        excel_file = 'used_tables_export.xlsx'
        df = pd.read_excel(excel_file, sheet_name='clinic_patients')
        
        print(f"Found {len(df)} records in Excel")
        
        db = SessionLocal()
        
        # تحميل البيانات
        inserted_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            try:
                trainee_no = str(row.get('trainee_no', '')).strip()
                
                # تخطي الصفوف الفارغة
                if not trainee_no or trainee_no == 'nan':
                    skipped_count += 1
                    continue
                
                # التحقق من وجود السجل
                existing = db.execute(
                    text("SELECT id FROM clinic_patients WHERE trainee_no=:trainee_no"),
                    {"trainee_no": trainee_no}
                ).fetchone()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # إدراج السجل الجديد
                insert_sql = """
                INSERT INTO clinic_patients (
                    record_kind, patient_type, trainee_no, full_name, national_id,
                    mobile, major, college, birth_date, department, gender,
                    address, email, visit_date, visit_reason, diagnosis,
                    treatment, notes
                ) VALUES (
                    :record_kind, :patient_type, :trainee_no, :full_name, :national_id,
                    :mobile, :major, :college, :birth_date, :department, :gender,
                    :address, :email, :visit_date, :visit_reason, :diagnosis,
                    :treatment, :notes
                )
                """
                
                db.execute(
                    text(insert_sql),
                    {
                        'record_kind': 'patient',
                        'patient_type': row.get('patient_type', 'trainee'),
                        'trainee_no': trainee_no,
                        'full_name': row.get('full_name', ''),
                        'national_id': str(row.get('national_id', '')).strip() or None,
                        'mobile': str(row.get('mobile', '')).strip() or None,
                        'major': row.get('major', ''),
                        'college': row.get('college', ''),
                        'birth_date': str(row.get('birth_date', '')).strip() or None,
                        'department': row.get('department', ''),
                        'gender': row.get('gender', ''),
                        'address': row.get('address', ''),
                        'email': row.get('email', ''),
                        'visit_date': str(row.get('visit_date', '')).strip() or None,
                        'visit_reason': row.get('visit_reason', ''),
                        'diagnosis': row.get('diagnosis', ''),
                        'treatment': row.get('treatment', ''),
                        'notes': row.get('notes', '')
                    }
                )
                
                inserted_count += 1
                print(f"  [{idx+1}] ✓ {row.get('full_name')} - {trainee_no}")
                
            except Exception as e:
                skipped_count += 1
                print(f"  [{idx+1}] ✗ Error: {str(e)}")
        
        db.commit()
        db.close()
        
        print(f"\n✓ Loaded {inserted_count} records")
        print(f"⊘ Skipped {skipped_count} records")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading data: {str(e)}")
        return False

def verify_table():
    """التحقق من الجدول والبيانات"""
    print("\nVerifying table...")
    try:
        db = SessionLocal()
        
        # التحقق من وجود الجدول
        result = db.execute(
            text("SELECT COUNT(*) as count FROM clinic_patients")
        ).fetchone()
        
        count = result[0] if result else 0
        print(f"✓ Table exists with {count} records")
        
        # عرض عينة من البيانات
        if count > 0:
            sample = db.execute(
                text("SELECT id, full_name, trainee_no, college FROM clinic_patients LIMIT 3")
            ).fetchall()
            
            print("\nSample records:")
            for record in sample:
                print(f"  - {record[1]} ({record[2]}) - {record[3]}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Error verifying table: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Clinic Patients Table Creator")
    print("=" * 60)
    
    # إنشاء الجدول
    if not create_clinic_patients_table():
        sys.exit(1)
    
    # تحميل البيانات
    if not load_clinic_patients_from_excel():
        sys.exit(1)
    
    # التحقق
    if not verify_table():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Clinic Patients table created and loaded successfully!")
    print("=" * 60)
