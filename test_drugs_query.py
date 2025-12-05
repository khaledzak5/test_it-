from app.database import SessionLocal, is_sqlite
from sqlalchemy import text

db = SessionLocal()
rows = db.execute(text(f"""
    SELECT id, trade_name, generic_name, strength, form
    FROM {'public.drugs' if not is_sqlite() else 'drugs'}
    WHERE is_active=TRUE
    ORDER BY trade_name
    LIMIT 100
""")).mappings().all()

for r in rows:
    trade = r.get('trade_name', '')
    generic = r.get('generic_name', '')
    strength = r.get('strength', '')
    form_val = r.get('form', '')
    parts = [x for x in [trade, generic, strength, form_val] if x]
    label = ' / '.join(parts)
    print(f'ID: {r["id"]}, Label: {label}')

print(f'\nTotal: {len(rows)} drugs')
db.close()
