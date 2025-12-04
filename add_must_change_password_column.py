import sqlite3
conn = sqlite3.connect("app.db")
conn.execute("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN NOT NULL DEFAULT 1;")
conn.commit()
conn.close()
print("تمت إضافة العمود must_change_password بنجاح.")
