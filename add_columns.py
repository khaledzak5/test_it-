from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
db = sessionmaker(bind=engine)()

# أضف الأعمدة المفقودة
cols_to_add = [
    ('created_by', 'INTEGER'),
    ('updated_at', 'TIMESTAMP'),
    ('visit_at', 'TIMESTAMP'),
    ('employee_no', 'TEXT'),
    ('temp_c', 'REAL'),
    ('bp_systolic', 'INTEGER'),
    ('bp_diastolic', 'INTEGER'),
    ('pulse_bpm', 'INTEGER'),
    ('resp_rpm', 'INTEGER'),
    ('weight_kg', 'REAL'),
    ('height_cm', 'REAL'),
    ('bmi', 'REAL'),
    ('glucose_mg', 'REAL'),
    ('o2_sat', 'INTEGER'),
    ('chronic_json', 'TEXT'),
    ('complaint', 'TEXT'),
    ('recommendation', 'TEXT'),
    ('rec_detail', 'TEXT'),
    ('rest_days', 'INTEGER'),
    ('rec_json', 'TEXT'),
    ('rx_json', 'TEXT'),
]

for col_name, col_type in cols_to_add:
    try:
        db.execute(text(f'ALTER TABLE clinic_patients ADD COLUMN {col_name} {col_type}'))
        print(f'✓ Added {col_name}')
    except Exception as e:
        print(f'⊘ {col_name}: {str(e)[:50]}')

db.commit()
db.close()
print('\n✓ Done!')
