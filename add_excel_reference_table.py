"""
إضافة جدول excel_data_references لقاعدة البيانات
"""

import sqlite3
import sys

DATABASE_PATH = 'app.db'

def add_excel_reference_table():
    """إضافة جدول المراجع من الإكسيل"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # التحقق من وجود الجدول
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='excel_data_references'
        """)
        
        if cursor.fetchone():
            print("✓ Table 'excel_data_references' already exists")
            conn.close()
            return True
        
        # إنشاء الجدول
        cursor.execute("""
            CREATE TABLE excel_data_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_type VARCHAR(50) NOT NULL,
                excel_id VARCHAR(255) NOT NULL,
                db_id INTEGER,
                excel_data TEXT,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(data_type, excel_id)
            )
        """)
        
        # إنشاء الفهارس
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_excel_ref_type_id 
            ON excel_data_references(data_type, excel_id)
        """)
        
        conn.commit()
        print("✓ Table 'excel_data_references' created successfully")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"✗ Error creating table: {str(e)}")
        return False

if __name__ == "__main__":
    if add_excel_reference_table():
        print("\nMigration completed successfully!")
        sys.exit(0)
    else:
        print("\nMigration failed!")
        sys.exit(1)
