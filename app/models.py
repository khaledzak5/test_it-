from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
    Float,
    ForeignKey,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship
from .database import Base

# =========================
# Department
# =========================
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)       # مثال: "تقنية إدارة أنظمة الشبكات - كلية نجران"
    college = Column(String(255), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    # (اختياري) ربط برئيس القسم كمستخدم
    head_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    head_user = relationship(
        "User",
        foreign_keys=[head_user_id],
        back_populates="headed_departments",
        lazy="joined",
    )

    # اسم رئيس القسم اليدوي (لو ما كان مستخدمًا)
    hod_name = Column(String(255), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_departments_name", "name"),
        Index("idx_departments_college", "college"),
    )

# =========================
# Course
# =========================
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    provider = Column(String(255), nullable=True)           # الجهة المنفّذة (قسم/وحدة)
    provider_name = Column(String(255), nullable=True)      # اسم المنفّذ (الشخص)
    hours = Column(Float, nullable=False)
    mode = Column(String(50), nullable=False)               # 'in_person'/'online' ... الخ
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    capacity = Column(Integer, default=30)
    registration_policy = Column(String(50), default="open")  # open|approval|waitlist
    prevent_duplicates = Column(Boolean, default=True)
    attendance_verification = Column(String(50), default="paper")  # paper|qr
    completion_threshold = Column(Integer, default=80)
    create_expected_roster = Column(Boolean, default=False)
    auto_issue_certificates = Column(Boolean, default=False)
    status = Column(String(50), default="published")  # draft|published|closed|finished
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_by_user_id = Column(Integer, nullable=True)

    # استهداف الأقسام (نصيًا)
    targets = relationship(
        "CourseTargetDepartment",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ✅ سجلّات المتدربين (للحضور/الكشوف)
    enrollments = relationship(
        "CourseEnrollment",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_courses_status", "status"),
        Index("idx_courses_range", "start_date", "end_date"),
    )

# =========================
# CourseTargetDepartment (pivot - نصّي)
# =========================
class CourseTargetDepartment(Base):
    __tablename__ = "course_target_departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    # ربط نصّي مع اسم القسم (مطابقة على departments.name و/أو sf01."Major")
    department_name = Column(String(255), nullable=False)

    course = relationship("Course", back_populates="targets")

    __table_args__ = (
        UniqueConstraint("course_id", "department_name", name="uq_course_target_name"),
        Index("idx_ctd_course_id", "course_id"),
        Index("idx_ctd_department_name", "department_name"),
    )

# =========================
# User
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    is_admin = Column(Boolean, default=False, nullable=False)   # سوبر أدمن (صلاحيات كاملة)
    is_college_admin = Column(Boolean, default=False, nullable=False)  # أدمن كلية (صلاحيات في نطاق كلية واحدة)
    college_admin_college = Column(String(255), nullable=True)  # الكلية التي يديرها أدمن الكلية
    is_hod = Column(Boolean, default=False, nullable=False)      # رئيس قسم؟
    is_doc = Column(Boolean, default=False, nullable=False)      # 👈 طبيب الكلية (جديد)
    hod_college = Column(String(255), nullable=True)             # كلية رئيس القسم (إن وُجد)

    is_active = Column(Boolean, default=True, nullable=False)
    must_change_password = Column(Boolean, default=True, nullable=False)  # يجب تغيير كلمة المرور عند أول دخول
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    headed_departments = relationship(
        "Department",
        back_populates="head_user",
        foreign_keys="Department.head_user_id",
        lazy="selectin",
    )

# =========================
# LoginLog
# =========================
class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(100), nullable=False)
    login_at = Column(DateTime, server_default=func.now(), nullable=False)
    ip_address = Column(String(50), nullable=True)

    user = relationship("User", backref="login_logs")

    __table_args__ = (
        Index("idx_login_logs_user_id", "user_id"),
        Index("idx_login_logs_login_at", "login_at"),
    )

# =========================
# College
# =========================
class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)                 # إنجليزي للطباعة
    name_print_ar = Column(String(255), nullable=True)           # عربي للطباعة (جديد)
    dean_name = Column(String(255), nullable=True)
    vp_students_name = Column(String(255), nullable=True)
    vp_trainers_name = Column(String(255), nullable=True)
    dean_sign_path = Column(Text, nullable=True)
    vp_students_sign_path = Column(Text, nullable=True)
    students_affairs_stamp_path = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

# =========================
# SystemSetting (KV store)
# =========================
class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, default="string")   # string|int|bool|json|text
    scope = Column(String(50), nullable=False, default="global")  # global أو لاحقًا college:<id>
    updated_by = Column(Integer, nullable=True)                   # user id (اختياري)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

# =========================
# CertificateTemplate
# =========================
class CertificateTemplate(Base):
    __tablename__ = "certificate_templates"

    id = Column(Integer, primary_key=True, index=True)
    scope = Column(String(50), nullable=False, default="global")  # global أو college:<id>
    name = Column(String(255), nullable=False)
    content_html = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    updated_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

# =========================
# CourseEnrollment
# =========================
class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    trainee_no = Column(String(50), nullable=False)

    # حقول لعرض البيانات مباشرة في الحضور
    trainee_name  = Column(String(150), nullable=True)
    trainee_major = Column(String(150), nullable=True)

    status = Column(String(50), nullable=False, default="registered")  # registered|completed|withdrawn...
    present = Column(Boolean, nullable=False, default=False)           # تأكيد الحضور

    certificate_code = Column(String(100), nullable=True)
    certificate_issued_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # علاقة ↔︎ Course
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint("course_id", "trainee_no", name="uq_enroll_course_trainee"),
        Index("idx_enroll_course", "course_id"),
        Index("idx_enroll_present", "present"),
        Index("idx_enroll_trainee_no", "trainee_no"),
    )
# =========================
# CertificateVerification
# =========================
class CertificateVerification(Base):
    __tablename__ = "certificate_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, nullable=False)
    trainee_no = Column(String(50), nullable=False)
    trainee_name = Column(String(150), nullable=True)
    course_title = Column(String(255), nullable=True)
    hours = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    certificate_code = Column(String(200), nullable=False)  # <seq>-<trainee_no>-<course_id>
    copy_no = Column(Integer, nullable=False, default=1)
    barcode_path = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("certificate_code", "copy_no", name="uq_cv_code_copy"),
        Index("idx_cv_code", "certificate_code"),
        Index("idx_cv_trainee", "trainee_no", "course_id"),
    )

# =========================
# ExcelDataReference - للربط مع ملف الإكسيل
# =========================
class ExcelDataReference(Base):
    __tablename__ = "excel_data_references"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(50), nullable=False)  # 'student', 'drug', 'patient', etc
    excel_id = Column(String(255), nullable=False)  # الرقم أو المعرف من الإكسيل
    db_id = Column(Integer, nullable=True)  # الرقم المقابل في قاعدة البيانات
    excel_data = Column(Text, nullable=True)  # بيانات JSON من الإكسيل
    imported_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_excel_ref_type_id", "data_type", "excel_id"),
        UniqueConstraint("data_type", "excel_id", name="uq_excel_ref_type_id"),
    )


# =========================
# FirstAidBox (صندوق الإسعافات)
# =========================
class FirstAidBox(Base):
    __tablename__ = "first_aid_boxes"

    id = Column(Integer, primary_key=True, index=True)
    box_name = Column(String(255), nullable=False)  # اسم الصندوق (مثلاً: "صندوق العيادة")
    location = Column(String(255), nullable=False)  # مكان الصندوق
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # العلاقات
    items = relationship("FirstAidBoxItem", back_populates="box", cascade="all, delete-orphan")
    created_by = relationship("User", foreign_keys=[created_by_user_id])

    __table_args__ = (
        Index("idx_first_aid_box_location", "location"),
    )


# =========================
# FirstAidBoxItem (محتويات الصندوق)
# =========================
class FirstAidBoxItem(Base):
    __tablename__ = "first_aid_box_items"

    id = Column(Integer, primary_key=True, index=True)
    box_id = Column(Integer, ForeignKey("first_aid_boxes.id", ondelete="CASCADE"), nullable=False)
    drug_name = Column(String(255), nullable=False)  # اسم الدواء/المادة
    drug_code = Column(String(100), nullable=True)  # رمز الدواء من الصيدلية
    quantity = Column(Integer, nullable=False, default=0)  # الكمية المتوفرة
    unit = Column(String(50), nullable=False, default="عدد")  # وحدة القياس (عدد، ملغ، إلخ)
    expiry_date = Column(Date, nullable=True)  # تاريخ الانتهاء
    notes = Column(Text, nullable=True)  # ملاحظات
    added_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # العلاقات
    box = relationship("FirstAidBox", back_populates="items")

    __table_args__ = (
        Index("idx_first_aid_item_box", "box_id"),
        Index("idx_first_aid_item_drug", "drug_code"),
    )


