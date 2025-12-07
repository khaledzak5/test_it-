import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Check columns in drug_transactions
cursor.execute("PRAGMA table_info(drug_transactions)")
cols = cursor.fetchall()

print("drug_transactions columns:")
for col in cols:
    print(f"  {col[1]}: {col[2]}")

conn.close()
