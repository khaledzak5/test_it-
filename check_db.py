from sqlalchemy import inspect, create_engine

engine = create_engine('sqlite:///app.db')
inspector = inspect(engine)

print("pharmacy_stock columns:")
cols = inspector.get_columns('pharmacy_stock')
for c in cols:
    print(f"  {c['name']}: {c['type']}")

print("\nwarehouse_stock columns:")
cols = inspector.get_columns('warehouse_stock')
for c in cols:
    print(f"  {c['name']}: {c['type']}")
