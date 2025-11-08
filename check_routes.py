"""
Check all registered API routes
"""

from app import app

print("=" * 80)
print("REGISTERED API ROUTES")
print("=" * 80)

routes = []
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': str(rule)
        })

# Sort by path
routes.sort(key=lambda x: x['path'])

# Group by category
categories = {
    '/api/auth': [],
    '/api/userAccount': [],
    '/api/userProfile': [],
    '/api/requests': [],
    '/api/shortlist': [],
    '/api/roles': []
}

for route in routes:
    path = route['path']
    categorized = False
    for category in categories:
        if path.startswith(category):
            categories[category].append(route)
            categorized = True
            break
    if not categorized and path.startswith('/api'):
        if 'other' not in categories:
            categories['other'] = []
        categories['other'].append(route)

# Print by category
for category, category_routes in categories.items():
    if category_routes:
        print(f"\n{category.upper()}")
        print("-" * 80)
        for route in category_routes:
            print(f"  {route['methods']:8} {route['path']}")

print("\n" + "=" * 80)
print(f"TOTAL ROUTES: {len(routes)}")
print("=" * 80)

