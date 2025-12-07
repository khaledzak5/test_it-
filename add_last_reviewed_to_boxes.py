#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add 'last_reviewed_at' column to first_aid_boxes table
"""
import sqlite3
from datetime import datetime

db_path = "app.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if last_reviewed_at column already exists
    cursor.execute("PRAGMA table_info(first_aid_boxes)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'last_reviewed_at' not in columns:
        # Add last_reviewed_at column
        cursor.execute(f"""
            ALTER TABLE first_aid_boxes 
            ADD COLUMN last_reviewed_at TIMESTAMP DEFAULT NULL
        """)
        conn.commit()
        print("✅ Successfully added 'last_reviewed_at' column to first_aid_boxes table")
    else:
        print("⚠️  'last_reviewed_at' column already exists in first_aid_boxes table")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
