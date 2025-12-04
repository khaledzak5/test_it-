from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# اختبر البحث
sql = """
    SELECT DISTINCT
        e.trainee_no,
        e.trainee_name,
        c.id as course_id,
        c.title as course_title,
        COUNT(*) as course_count
    FROM course_enrollments e
    INNER JOIN courses c ON e.course_id = c.id
    GROUP BY e.trainee_no
    LIMIT 3
"""

query = text(sql)
results = db.execute(query).mappings().all()

print(f"عدد النتائج: {len(results)}")
for row in results:
    print(f"  {row['trainee_no']} - {row['trainee_name']} ({row['course_count']} دورات)")

db.close()
