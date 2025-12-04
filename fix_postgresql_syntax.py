"""إصلاح جميع بنية PostgreSQL في clinic.py"""
import re

with open('app/routers/clinic.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. إزالة NULL::text
print("إزالة NULL::text...")
content = content.replace('NULL::text', 'NULL')

# 2. إزالة (now() - make_interval...)::date
print("إزالة ::date من now()...")
content = re.sub(
    r'\(\s*now\(\)\s*-\s*make_interval\(years\s*=>\s*:y\)\)\s*::\s*date',
    '(now() - make_interval(years => :y))',
    content
)

# 3. إزالة :: من json columns
print("إزالة :: من CAST للـ JSON...")
content = content.replace('::chronic,', ':chronic,')
content = content.replace('::rec_json,', ':rec_json,')
content = content.replace('::rec_json)', ':rec_json)')
content = content.replace('::rx_json,', ':rx_json,')
content = content.replace('::rx_json)', ':rx_json)')

# 4. إزالة CAST(...AS jsonb)
print("إزالة CAST(...AS jsonb)...")
content = re.sub(r'CAST\(([^)]+)\s+AS\s+jsonb\)', r'\1', content)

with open('app/routers/clinic.py', 'w', encoding='utf-8') as f:
    f.write(content)

# تحقق
with open('app/routers/clinic.py', 'r', encoding='utf-8') as f:
    final = f.read()
    
remaining_double = len(re.findall(r'::', final))
remaining_cast = len(re.findall(r'CAST\(.*?AS', final))
remaining_make_interval = len(re.findall(r'make_interval', final))

print(f'\n✓ تم إصلاح جميع البيانات!')
print(f':: المتبقية: {remaining_double}')
print(f'CAST المتبقية: {remaining_cast}')
print(f'make_interval المتبقية: {remaining_make_interval}')
