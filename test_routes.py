from app.main import app

routes = []
for route in app.routes:
    if hasattr(route, 'path'):
        routes.append(route.path)

skills_routes = [r for r in routes if 'skills' in r]
print("All skills routes:")
for r in sorted(skills_routes):
    print(f"  {r}")

print(f"\nTotal routes: {len(routes)}")
