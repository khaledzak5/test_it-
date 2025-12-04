from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./app.db')
inspector = inspect(engine)
columns = inspector.get_columns('clinic_patients')

print('Columns in clinic_patients:')
for col in columns:
    print(f'  - {col["name"]}: {col["type"]}')

# Try to get schema of the table
db = sessionmaker(bind=engine)()
result = db.execute(text("PRAGMA table_info(clinic_patients)"))
print("\nPRAGMA table_info result:")
for row in result:
    print(f"  {row}")
