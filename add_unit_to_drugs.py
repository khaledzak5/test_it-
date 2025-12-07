#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add 'unit' column to drugs table
"""
import sqlite3

db_path = "app.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if unit column already exists
    cursor.execute("PRAGMA table_info(drugs)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'unit' not in columns:
        # Add unit column with default value
        cursor.execute("ALTER TABLE drugs ADD COLUMN unit VARCHAR(50) DEFAULT NULL")
        conn.commit()
        print("✅ Successfully added 'unit' column to drugs table")
    else:
        print("⚠️  'unit' column already exists in drugs table")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
