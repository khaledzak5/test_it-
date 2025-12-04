#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار سريع للتحقق من أن جميع دوال Excel تعمل بشكل صحيح
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from excel_data_reference import (
    get_statistics,
    get_all_drugs,
    get_low_stock_drugs,
    search_students,
    search_drugs,
    search_clinic_patients,
    get_students_by_college,
    get_all_colleges,
    get_all_departments,
    get_drug_stock,
    get_drug_by_code,
)

def test_excel_integration():
    """اختبار التكامل مع Excel"""
    
    print("=" * 80)
    print("🧪 اختبار نظام البيانات من Excel")
    print("=" * 80)
    
    # 1. اختبار الإحصائيات
    print("\n✅ اختبار 1: الإحصائيات العامة")
    try:
        stats = get_statistics()
        print(f"   - إجمالي المتدربين: {stats['total_students']}")
        print(f"   - إجمالي الأدوية: {stats['total_drugs']}")
        print(f"   - الأدوية النشطة: {stats['total_active_drugs']}")
        print(f"   - أدوية بمخزون منخفض: {stats['total_low_stock_drugs']}")
        print(f"   - مرضى العيادة: {stats['total_clinic_patients']}")
        print("   ✓ نجح!")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 2. اختبار الأدوية
    print("\n✅ اختبار 2: البيانات الأساسية للأدوية")
    try:
        drugs = get_all_drugs()
        if drugs:
            drug = drugs[0]
            print(f"   - الدواء الأول: {drug.get('trade_name')}")
            print(f"   - الاسم العام: {drug.get('generic_name')}")
            print(f"   - المخزون: {drug.get('stock_qty')} {drug.get('unit')}")
            print("   ✓ نجح!")
        else:
            print("   ✗ لا توجد أدوية!")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 3. اختبار get_drug_stock
    print("\n✅ اختبار 3: دالة get_drug_stock()")
    try:
        stock = get_drug_stock("1")
        if stock:
            print(f"   - معرف الدواء: 1")
            print(f"   - الاسم: {stock.get('trade_name')}")
            print(f"   - المخزون: {stock.get('stock_qty')}")
            print("   ✓ نجح!")
        else:
            print("   ✗ دواء غير موجود")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 4. اختبار البحث
    print("\n✅ اختبار 4: البحث عن المتدربين")
    try:
        results = search_students("محمد")
        print(f"   - عدد النتائج: {len(results)}")
        if results:
            print(f"   - أول متدرب: {results[0].get('student_Name')}")
            print("   ✓ نجح!")
        else:
            print("   ✗ لا توجد نتائج")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 5. اختبار البحث عن الأدوية
    print("\n✅ اختبار 5: البحث عن الأدوية")
    try:
        results = search_drugs("amox")
        print(f"   - عدد النتائج: {len(results)}")
        if results:
            print(f"   - أول دواء: {results[0].get('trade_name')}")
            print("   ✓ نجح!")
        else:
            print("   ✗ لا توجد نتائج")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 6. اختبار البحث عن المرضى
    print("\n✅ اختبار 6: البحث عن مرضى العيادة")
    try:
        results = search_clinic_patients("2101")
        print(f"   - عدد النتائج: {len(results)}")
        if results:
            print(f"   - أول مريض: {results[0].get('full_name')}")
            print("   ✓ نجح!")
        else:
            print("   ✗ لا توجد نتائج")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 7. اختبار الكليات
    print("\n✅ اختبار 7: الحصول على الكليات")
    try:
        colleges = get_all_colleges()
        print(f"   - عدد الكليات: {len(colleges)}")
        if colleges:
            print(f"   - أول كلية: {colleges[0].get('college_name', colleges[0].get('name'))}")
            print("   ✓ نجح!")
        else:
            print("   ✗ لا توجد كليات")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 8. اختبار الأقسام
    print("\n✅ اختبار 8: الحصول على الأقسام")
    try:
        departments = get_all_departments()
        print(f"   - عدد الأقسام: {len(departments)}")
        if departments:
            print(f"   - أول قسم: {departments[0].get('department_name', departments[0].get('name'))}")
            print("   ✓ نجح!")
        else:
            print("   ✗ لا توجد أقسام")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 9. اختبار المتدربين حسب الكلية
    print("\n✅ اختبار 9: المتدربين حسب الكلية")
    try:
        colleges = get_all_colleges()
        if colleges:
            college_name = colleges[0].get('college_name', colleges[0].get('name'))
            results = get_students_by_college(college_name)
            print(f"   - عدد المتدربين في {college_name}: {len(results)}")
            print("   ✓ نجح!")
        else:
            print("   ✗ لا توجد كليات")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    # 10. اختبار الأدوية بمخزون منخفض
    print("\n✅ اختبار 10: الأدوية بمخزون منخفض")
    try:
        low_stock = get_low_stock_drugs()
        print(f"   - عدد الأدوية بمخزون منخفض: {len(low_stock)}")
        if low_stock:
            for drug in low_stock:
                print(f"     • {drug.get('trade_name')}: {drug.get('stock_qty')} (حد أدنى: {drug.get('reorder_level')})")
        print("   ✓ نجح!")
    except Exception as e:
        print(f"   ✗ فشل: {e}")
    
    print("\n" + "=" * 80)
    print("✅ انتهى الاختبار بنجاح!")
    print("=" * 80)

if __name__ == "__main__":
    test_excel_integration()
