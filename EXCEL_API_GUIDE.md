# 📚 دليل استخدام Excel API

هذا الدليل يشرح كيفية استخدام جميع الواجهات البرمجية المتاحة للوصول إلى بيانات Excel.

## 🔑 المتطلبات الأساسية

- كل API يتطلب مستخدم مصرح (أي يجب أن تكون قد سجلت الدخول)
- الأدمن يحصل على كل شيء
- الأطباء يحصلون على البيانات الطبية

## 📊 الإحصائيات

### 1. الإحصائيات العامة الشاملة
```
GET /api/excel/statistics
```

**الاستجابة:**
```json
{
  "success": true,
  "statistics": {
    "total_students": 2571,
    "total_drugs": 5,
    "total_active_drugs": 5,
    "total_low_stock_drugs": 0,
    "total_clinic_patients": 23,
    "total_courses": 6,
    "total_departments": 11,
    "total_colleges": 4,
    "total_users": 3
  }
}
```

### 2. الإحصائيات حسب الكلية
```
GET /api/excel/statistics/by-college/{college_name}
```

**مثال:**
```
GET /api/excel/statistics/by-college/الهندسة
```

**الاستجابة:**
```json
{
  "success": true,
  "statistics": {
    "students_count": 650,
    "clinic_patients_count": 8,
    "majors": ["البرمجة", "الشبكات", "قواعد البيانات"]
  }
}
```

### 3. الإحصائيات حسب القسم
```
GET /api/excel/statistics/by-department/{department_name}
```

## 👥 المتدربين

### 1. البحث العام
```
GET /api/excel/students/search?q={query}&limit={limit}
```

**المعاملات:**
- `q`: نص البحث (إلزامي، بحد أدنى 1 حرف)
- `limit`: عدد النتائج (اختياري، افتراضي 10، أقصى 100)

**الاستجابة:**
```json
{
  "success": true,
  "count": 2,
  "results": [
    {
      "student_id": "2101024",
      "student_Name": "محمد أحمد علي",
      "Major": "البرمجة",
      "College": "الهندسة",
      "Department": "الحاسوب",
      "Phone": "0123456789",
      "Email": "student@example.com"
    }
  ]
}
```

### 2. الحصول على متدرب محدد
```
GET /api/excel/students/{student_id}
```

### 3. المتدربين حسب الكلية
```
GET /api/excel/students/by-college/{college_name}
```

**مثال:**
```
GET /api/excel/students/by-college/الهندسة
```

### 4. المتدربين حسب التخصص
```
GET /api/excel/students/by-major/{major_name}
```

**مثال:**
```
GET /api/excel/students/by-major/البرمجة
```

### 5. المتدربين حسب الحالة
```
GET /api/excel/students/by-status/{status}
```

**الحالات المدعومة:**
- `active` - متدربين نشطين
- `graduated` - خريجين
- `retired` - متقاعدين

## 💊 الأدوية

### 1. جميع الأدوية
```
GET /api/excel/drugs/all
```

**الاستجابة:**
```json
{
  "success": true,
  "count": 5,
  "drugs": [
    {
      "id": 1,
      "trade_name": "Amoxicillin 500",
      "generic_name": "Amoxicillin",
      "strength": "500mg",
      "form": "أقراص",
      "unit": "عدد",
      "stock_qty": 100,
      "reorder_level": 20,
      "is_active": true,
      "manufacturer": "Pharma Co"
    }
  ]
}
```

### 2. البحث عن أدوية
```
GET /api/excel/drugs/search?name={drug_name}
```

**مثال:**
```
GET /api/excel/drugs/search?name=Amoxicillin
```

### 3. البحث المتقدم
```
GET /api/excel/drugs/search/advanced?query={query}
```

يبحث في الاسم التجاري والاسم العام معاً.

### 4. الأدوية ذات المخزون المنخفض
```
GET /api/excel/drugs/low-stock?threshold={threshold}
```

**المعاملات:**
- `threshold`: الحد الأدنى (اختياري، إذا لم يتم تحديده يستخدم reorder_level)

**مثال:**
```
GET /api/excel/drugs/low-stock
```

يرجع جميع الأدوية التي stock_qty <= reorder_level

### 5. الأدوية حسب الحالة
```
GET /api/excel/drugs/status/{status}
```

**الحالات:**
- `active` أو `true` - أدوية نشطة
- `inactive` أو `false` - أدوية غير نشطة

## 🏥 مرضى العيادة

### 1. البحث عن مريض
```
GET /api/excel/clinic/search?query={query}&limit={limit}
```

يبحث باسم المريض أو رقم متدربه.

### 2. الحصول على بيانات مريض
```
GET /api/excel/clinic/patients/{trainee_no}
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "trainee_no": "2101024",
    "full_name": "محمد أحمد علي",
    "age": 25,
    "gender": "ذكر",
    "college": "الهندسة",
    "department": "الحاسوب",
    "visit_date": "2025-01-15",
    "chief_complaint": "صداع وحمى",
    "diagnosis": "نزلة برد",
    "prescribed_medication": "Paracetamol 500mg"
  }
}
```

## 🏢 الكليات والأقسام

### 1. جميع الكليات
```
GET /api/excel/colleges/all
```

### 2. جميع الأقسام
```
GET /api/excel/departments/all
```

### 3. أقسام كلية معينة
```
GET /api/excel/departments/by-college/{college_name}
```

### 4. دورات قسم معين
```
GET /api/excel/courses/by-department/{department_name}
```

## 🔄 أمثلة الاستخدام

### استخدام JavaScript

```javascript
// البحث عن متدرب
fetch('/api/excel/students/search?q=محمد&limit=5')
  .then(r => r.json())
  .then(data => console.log(data.results));

// الحصول على الأدوية ذات المخزون المنخفض
fetch('/api/excel/drugs/low-stock')
  .then(r => r.json())
  .then(data => console.log('Low stock drugs:', data.drugs));

// الإحصائيات حسب الكلية
fetch('/api/excel/statistics/by-college/الهندسة')
  .then(r => r.json())
  .then(data => console.log('Engineering stats:', data.statistics));
```

### استخدام Python

```python
import requests

BASE_URL = "http://localhost:8000/api/excel"
HEADERS = {"Authorization": "Bearer YOUR_TOKEN"}  # إذا لزم الأمر

# البحث عن متدرب
response = requests.get(f"{BASE_URL}/students/search", params={"q": "محمد", "limit": 5})
print(response.json())

# الأدوية ذات المخزون المنخفض
response = requests.get(f"{BASE_URL}/drugs/low-stock")
print(response.json())

# الإحصائيات
response = requests.get(f"{BASE_URL}/statistics")
print(response.json())
```

### استخدام CURL

```bash
# البحث عن متدرب
curl -X GET "http://localhost:8000/api/excel/students/search?q=محمد"

# جميع الأدوية
curl -X GET "http://localhost:8000/api/excel/drugs/all"

# الإحصائيات
curl -X GET "http://localhost:8000/api/excel/statistics"
```

## 📝 ملاحظات مهمة

1. **الترميز:** جميع البيانات ترجع بصيغة UTF-8 JSON
2. **معالجة الأخطاء:** إذا كانت `success` قيمتها `false`، هناك `error` يحتوي على رسالة الخطأ
3. **الصلاحيات:** يجب أن تكون مصرحاً للوصول إلى أي API
4. **الأداء:** البيانات مخزنة في الذاكرة (Cache) للأداء السريع
5. **الحدود:** بعض الـ APIs لديها حد أقصى للنتائج (مثل limit=100 للبحث)

## 🔗 الروابط السريعة

- `/admin/excel-data` - لوحة البيانات الشاملة (للأدمن فقط)
- `/api/excel/*` - جميع الـ APIs

## ❓ الأسئلة الشائعة

**س: هل يمكنني تعديل بيانات Excel من خلال API؟**
ج: لا، البيانات قراءة فقط. يتم تحديث المخزون من خلال عمليات النظام (مثل صرف أدوية).

**س: كم مرة يتم تحديث البيانات من Excel؟**
ج: عند بدء التطبيق يتم تحميلها مرة واحدة. لتحديث البيانات يجب إعادة تشغيل التطبيق.

**س: ماذا لو كانت قاعدة البيانات تحتوي على بيانات مختلفة عن Excel؟**
ج: Excel هو المصدر الأساسي للبيانات المرجعية. قاعدة البيانات تحتوي على السجلات الجديدة والعمليات.
