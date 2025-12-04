# Excel Data Integration - دليل الاستخدام

## نظرة عامة
تم دمج ملف الإكسيل `used_tables_export.xlsx` مع نظام إدارة الدورات التدريبية. يمكن الآن البحث عن بيانات المتدربين والأدوية والمرضى مباشرة من الملف.

## الملفات المضافة

### 1. `excel_data_reference.py` (الملف الرئيسي)
مكتبة Python تحتوي على جميع دوال البحث والوصول إلى بيانات الإكسيل:
- تحميل البيانات مرة واحدة وتخزينها في الذاكرة لتحسين الأداء
- دوال للبحث عن المتدربين والأدوية والمرضى
- دعم البحث النصي والفلترة

### 2. `app/routers/excel_api.py`
API endpoints للبحث في بيانات الإكسيل:
```
GET /api/excel/students/search?q=اسم  - البحث عن متدرب
GET /api/excel/students/{student_id}   - الحصول على بيانات متدرب محددة
GET /api/excel/drugs/all              - قائمة جميع الأدوية
GET /api/excel/drugs/search?name=...   - البحث عن دواء
GET /api/excel/clinic/patients/{trainee_no} - بيانات المريض
GET /api/excel/statistics             - إحصائيات البيانات
```

### 3. `add_excel_reference_table.py`
سكريبت لإضافة جدول `excel_data_references` لقاعدة البيانات

## الدوال الرئيسية

### البحث عن المتدربين
```python
from excel_data_reference import get_student_by_id, search_students

# البحث بواسطة رقم المتدرب
student = get_student_by_id("2101024")

# البحث النصي
results = search_students("أحمد محمد")
```

### البحث عن الأدوية
```python
from excel_data_reference import get_drug_by_name, get_all_drugs

# البحث باسم الدواء
drug = get_drug_by_name("Amoxicillin")

# الحصول على جميع الأدوية
all_drugs = get_all_drugs()
```

### البحث عن المرضى
```python
from excel_data_reference import get_clinic_patient_by_trainee_no, get_clinic_patients_by_college

# البحث بواسطة رقم المتدرب
patient = get_clinic_patient_by_trainee_no("2101024")

# الحصول على مرضى كلية معينة
patients = get_clinic_patients_by_college("كلية الهندسة")
```

## الإحصائيات

### الأوراق الموجودة في الملف
1. **sf01** - 2571 متدرب
2. **clinic_patients** - 23 مريض من سجل العيادة
3. **drugs** - 5 أدوية
4. **courses** - 6 دورات تدريبية
5. **departments** - 11 قسم
6. **colleges** - 4 كليات
7. **users** - 3 مستخدمين
8. **drug_movements** - 26 حركة أدوية
9. **locations** - 3 مواقع

## أمثلة الاستخدام

### في قالب HTML (Jinja2)
```html
<!-- يمكن استخدام API endpoints مع JavaScript -->
<script>
  fetch('/api/excel/students/2101024')
    .then(r => r.json())
    .then(data => {
      console.log(data.data); // بيانات المتدرب
    });
</script>
```

### في مسار FastAPI
```python
from fastapi import FastAPI, Depends
from excel_data_reference import get_student_by_id

@app.get("/my-route")
def my_route(student_id: str, user=Depends(require_doc)):
    student_data = get_student_by_id(student_id)
    if student_data:
        return {"success": True, "student": student_data}
    return {"success": False, "error": "Student not found"}
```

## الربط مع الدوال الموجودة

### مثال: عند إضافة متدرب في دورة، اعرض بياناته من الإكسيل
```python
def add_trainee_to_course(course_id: int, trainee_no: str):
    from excel_data_reference import get_student_by_id
    
    # احصل على بيانات المتدرب من الإكسيل
    student = get_student_by_id(trainee_no)
    
    if student:
        # استخدم البيانات لملء معلومات المتدرب
        enrollment = CourseEnrollment(
            course_id=course_id,
            trainee_no=trainee_no,
            trainee_name=student.get('student_Name'),
            trainee_major=student.get('Major'),
        )
        db.add(enrollment)
        db.commit()
```

## ملاحظات مهمة

1. **الأداء**: البيانات تُحمّل مرة واحدة في الذاكرة عند بدء التطبيق
2. **التحديثات**: إذا تم تحديث ملف الإكسيل، يجب إعادة تشغيل التطبيق
3. **البحث**: جميع عمليات البحث تُجرى من الذاكرة بدون اتصال بقاعدة البيانات
4. **الأمان**: جميع endpoints تتطلب مصادقة (require_doc)

## المستقبل

يمكن توسيع النظام بـ:
- مزامنة تلقائية لملف الإكسيل
- إضافة صفحات واجهة للبحث المتقدم
- ربط البيانات بشكل تلقائي عند إنشاء سجلات جديدة
- تقرير مقارنة بين بيانات الإكسيل وقاعدة البيانات
