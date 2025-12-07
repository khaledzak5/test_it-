import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE drug_transactions ADD COLUMN expiry_date DATE DEFAULT NULL')
    conn.commit()
    print('✅ expiry_date column added successfully')
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print('ℹ️ Column already exists')
    else:
        print(f'❌ Error: {e}')
finally:
    conn.close()
