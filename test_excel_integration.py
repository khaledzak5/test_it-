"""
سكريبت اختبار نظام دمج بيانات الإكسيل
"""

import sys
sys.path.insert(0, '.')

from excel_data_reference import (
    load_excel_data,
    get_student_by_id,
    get_drug_by_name,
    get_clinic_patient_by_trainee_no,
    search_students,
    get_all_drugs,
    get_statistics,
)

print("=" * 80)
print("Excel Data Integration Test")
print("=" * 80)

# تحميل البيانات
print("\n1. Loading Excel data...")
load_excel_data()
print("   [OK] Data loaded successfully")

# الإحصائيات
print("\n2. Statistics:")
stats = get_statistics()
for key, value in stats.items():
    print(f"   - {key}: {value}")

# اختبار البحث عن المتدربين
print("\n3. Testing Student Search:")
print("   a) Finding student by ID (2101024)...")
student = get_student_by_id("2101024")
if student:
    print(f"      Found: {student.get('student_Name')} - {student.get('College')}")
else:
    print("      Not found")

print("\n   b) Searching for students with 'Ahmed'...")
results = search_students("Ahmed")
print(f"      Found {len(results)} results")
if results:
    print(f"      First result: {results[0].get('student_Name')}")

# اختبار البحث عن الأدوية
print("\n4. Testing Drug Search:")
drugs = get_all_drugs()
print(f"   Total drugs: {len(drugs)}")
if drugs:
    print(f"   First drug: {drugs[0].get('trade_name')} - {drugs[0].get('generic_name')}")

# اختبار البحث عن المرضى
print("\n5. Testing Patient Search:")
patients = [
    get_clinic_patient_by_trainee_no("2101024"),
    get_clinic_patient_by_trainee_no("2101001"),
]
for patient in patients:
    if patient:
        print(f"   Found: {patient.get('full_name')} - {patient.get('trainee_no')}")

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
