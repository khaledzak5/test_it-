import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# إنشاء جدول login_logs
cursor.execute("""
CREATE TABLE IF NOT EXISTS login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username VARCHAR(100) NOT NULL,
    login_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# إنشاء الفهارس
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON login_logs(user_id);
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_login_logs_login_at ON login_logs(login_at);
""")

conn.commit()
conn.close()
print("تمت إضافة جدول login_logs بنجاح.")
