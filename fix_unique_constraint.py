from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
db = sessionmaker(bind=engine)()

# SQLite لا يدعم DROP CONSTRAINT، يجب إعادة إنشاء الجدول
# الخطة: 
# 1. انقل البيانات الموجودة إلى جدول مؤقت
# 2. احذف الجدول الأصلي
# 3. أنشئ جدول جديد بدون UNIQUE على trainee_no
# 4. أعد البيانات

print("جاري إعادة هيكلة الجدول...")

# احفظ البيانات
db.execute(text('CREATE TABLE clinic_patients_backup AS SELECT * FROM clinic_patients'))
print("✓ تم حفظ البيانات")

# احذف الجدول القديم
db.execute(text('DROP TABLE clinic_patients'))
print("✓ تم حذف الجدول القديم")

# أنشئ جدول جديد بدون UNIQUE على trainee_no
db.execute(text('''
    CREATE TABLE clinic_patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_kind TEXT NOT NULL DEFAULT 'patient',
        patient_type TEXT,
        trainee_no TEXT,
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        updated_at TIMESTAMP,
        visit_at TIMESTAMP,
        employee_no TEXT,
        temp_c REAL,
        bp_systolic INTEGER,
        bp_diastolic INTEGER,
        pulse_bpm INTEGER,
        resp_rpm INTEGER,
        weight_kg REAL,
        height_cm REAL,
        bmi REAL,
        glucose_mg REAL,
        o2_sat INTEGER,
        chronic_json TEXT,
        complaint TEXT,
        recommendation TEXT,
        rec_detail TEXT,
        rest_days INTEGER,
        rec_json TEXT,
        rx_json TEXT
    )
'''))
print("✓ تم إنشاء جدول جديد")

# أعد البيانات
db.execute(text('''
    INSERT INTO clinic_patients 
    SELECT * FROM clinic_patients_backup
'''))
db.commit()
print("✓ تم استرجاع البيانات")

# احذف الجدول المؤقت
db.execute(text('DROP TABLE clinic_patients_backup'))
db.commit()
print("✓ تم تنظيف الجداول المؤقتة")

print("\n✅ تم إعادة هيكلة الجدول بنجاح - لا يوجد UNIQUE constraint على trainee_no")

db.close()
