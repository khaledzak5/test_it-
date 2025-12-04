# app/main.py
import os
import time
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse, Response, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette import status
from app.routers import verify

# ── الإعدادات ─────────────────────────────────────────────
load_dotenv()
APP_NAME = os.getenv("APP_NAME", "Training Courses System")
DEBUG = os.getenv("DEBUG", "true").strip().lower() in ("1", "true", "yes")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
SESSION_MAX_AGE_DAYS = int(os.getenv("SESSION_MAX_AGE_DAYS", "7"))
SLIDING_TOUCH_SECONDS = 15 * 60  # 15 دقيقة
HTTPS_ONLY = os.getenv("HTTPS_ONLY", "false").strip().lower() in ("1", "true", "yes")

# ── ORM ──────────────────────────────────────────────────
from .database import Base, engine, SessionLocal  # noqa: E402
from . import models  # noqa: E402
from .services import settings as S  # noqa: E402

# ── Routers ──────────────────────────────────────────────
from .routers import auth as auth_router                    # /auth/...
from .routers import hod as hod_router                      # /hod/...
from .routers import admin as admin_router                  # /admin/... (لوحة الأدمن العامة/القديمة)
from .routers import admin_users as admin_users_router      # /admin/users/...
from .routers import admin_departments as admin_departments_router  # /admin/departments
from .routers import admin_colleges as admin_colleges_router        # /admin/colleges
from .routers import admin_settings as admin_settings_router        # /admin/settings
from .routers import clinic as clinic_router
from .routers import pharmacy as pharmacy_router
from .routers import first_aid as first_aid_router
from .routers import inventory as inventory_router
from .routers import profile as profile_router              # /profile/... (الملف الشخصي)
from .routers import excel_api as excel_api_router         # /api/excel/... (Excel Data API)
# ── Middlewares ──────────────────────────────────────────
from .middlewares.maintenance import MaintenanceMiddleware  # وضع الصيانة

# ── إنشاء التطبيق ───────────────────────────────────────
app = FastAPI(title=APP_NAME, debug=DEBUG)

# 1) نضيف SessionMiddleware أخيرًا ليكون هو الخارجي (يُنفّذ أولًا)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=SESSION_MAX_AGE_DAYS * 24 * 3600,
    same_site="lax",
    https_only=HTTPS_ONLY,  # اجعل HTTPS_ONLY=1 في الإنتاج مع HTTPS
)

# 2) MaintenanceMiddleware (سيحصل على الجلسة من الميدلوير الخارجي)
app.add_middleware(MaintenanceMiddleware)

# 3) ميدلوير يحقن current_user + إعدادات الواجهة في كل TemplateResponse
class SessionHelperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session = request.scope.get("session") or {}
        request.state.current_user = session.get("user")

        # تجديد انزلاقي
        if session:
            try:
                last_touch = session.get("last_touch", 0)
                now = int(time.time())
                if now - last_touch >= SLIDING_TOUCH_SECONDS:
                    session["last_touch"] = now
            except Exception:
                pass

        response = await call_next(request)

        # حقن current_user + إعدادات الواجهة في سياق القالب إن وجد
        try:
            if hasattr(response, "template") and hasattr(response, "context") and isinstance(response.context, dict):
                # المستخدم
                if request.state.current_user:
                    response.context.setdefault("current_user", request.state.current_user)
                else:
                    response.context.setdefault("current_user", None)

                # إعدادات واجهة عامة (اسم النظام والشعار والفافيكون والتذييل)
                db = SessionLocal()
                try:
                    app_name       = S.get_str(db, "app.name", "Training Courses System")
                    ui_footer      = S.get_str(db, "ui.footer_text", "")
                    ui_logo_url    = S.get_str(db, "ui.logo_url", "")
                    ui_favicon_url = S.get_str(db, "ui.favicon_url", "")
                finally:
                    db.close()

                response.context.setdefault("app_name", app_name)
                response.context.setdefault("ui_footer", ui_footer)
                response.context.setdefault("ui_logo_url", ui_logo_url)
                response.context.setdefault("ui_favicon_url", ui_favicon_url)
        except Exception:
            pass

        return response

app.add_middleware(SessionHelperMiddleware)

# ── Static & Templates ───────────────────────────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# إضافة فلاتر مخصصة
from jinja2 import Environment
def first_letter(text):
    """استخراج أول حرف من النص"""
    if not text:
        return "؟"
    return str(text)[0].upper()

# تسجيل الفلتر
templates.env.filters['first_letter'] = first_letter
import itertools

def _flatten_filter(value):
    """Flatten an iterable of iterables into a single list for Jinja templates.

    - Treats strings as atomic (not iterables to flatten).
    - Skips None values.
    """
    try:
        def to_iter(x):
            if x is None:
                return []
            if isinstance(x, (str, bytes)):
                return [x]
            try:
                iter(x)
                return x
            except TypeError:
                return [x]

        return list(itertools.chain.from_iterable(to_iter(v) for v in value))
    except Exception:
        return []

templates.env.filters['flatten'] = _flatten_filter

# ── إنشاء الجداول (مرة أولى) ────────────────────────────
Base.metadata.create_all(bind=engine)

# ── تضمين الراوترات (⚠️ الترتيب يهم) ────────────────────
app.include_router(auth_router.router)
app.include_router(profile_router.router)  # الملف الشخصي
app.include_router(hod_router.router)

# المسارات المتخصصة أولًا
app.include_router(admin_users_router.router)         # /admin/users
app.include_router(admin_departments_router.router)   # /admin/departments
app.include_router(admin_colleges_router.router)      # /admin/colleges
app.include_router(admin_settings_router.router)      # /admin/settings
app.include_router(clinic_router.router)
app.include_router(pharmacy_router.router)
app.include_router(first_aid_router.router)
app.include_router(inventory_router.router)
app.include_router(excel_api_router.router)            # Excel Data API
app.include_router(verify.router)
# ثم الراوتر العام
app.include_router(admin_router.router)               # /admin/...

# ────────────────────────────────────────────────────────
# PDF Export for Skills Record (direct endpoint)
# ────────────────────────────────────────────────────────
@app.get("/hod/skills-record-pdf/{trainee_no}")
def export_skills_record_pdf(trainee_no: str):
    """Export trainee skills record as PDF"""
    try:
        from sqlalchemy import text
        from xhtml2pdf import pisa
        
        db = SessionLocal()
        
        # Simple query
        query = text(f"""
        SELECT trainee_no, trainee_name 
        FROM course_enrollments 
        WHERE trainee_no = '{trainee_no}' 
        LIMIT 1
        """)
        result = db.execute(query).first()
        
        if not result:
            db.close()
            return PlainTextResponse("متدرب غير موجود", status_code=404)
        
        # Create simple HTML
        html_str = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تقرير</title>
        </head>
        <body>
            <h1>تقرير سجل المهارات</h1>
            <p>الرقم: {result[0]}</p>
            <p>الاسم: {result[1]}</p>
        </body>
        </html>
        """
        
        # Generate PDF
        pdf_bytes = io.BytesIO()
        pisa.CreatePDF(html_str.encode('utf-8'), dest=pdf_bytes)
        pdf_bytes.seek(0)
        db.close()
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{trainee_no}.pdf"}
        )
    except Exception as e:
        return PlainTextResponse(f"خطأ: {str(e)}", status_code=500)

# ── /health (اختياري) ───────────────────────────────────
@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}

# ── favicon ─────────────────────────────────────────────
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    path = "app/static/images/favicon.ico"
    if os.path.exists(path):
        return FileResponse(path)
    return Response(status_code=204)

# ── Handlers ────────────────────────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url=f"/auth/login?next={request.url.path}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        if request.url.path == "/favicon.ico":
            return Response(status_code=404)
        return PlainTextResponse("الصفحة غير موجودة", status_code=404)
    return PlainTextResponse(str(exc.detail or "خطأ"), status_code=exc.status_code)

# ── الصفحة الرئيسية الذكية ───────────────────────────────
@app.get("/", include_in_schema=False)
def index(request: Request):
    u = (request.scope.get("session") or {}).get("user")
    if not u:
        return RedirectResponse("/auth/login", status_code=303)

    is_admin = bool(u.get("is_admin"))
    is_hod   = bool(u.get("is_hod"))
    is_doc   = bool(u.get("is_doc"))

    # أولوية التوجيه: طبيب → العيادة، ثم هود، ثم أدمن
    if is_doc:
        return RedirectResponse("/clinic/", status_code=303)
    if is_hod:
        return RedirectResponse("/hod/", status_code=303)
    if is_admin:
        return RedirectResponse("/admin/", status_code=303)

    # افتراضيًا (مستخدم عادي): أعد توجيهه للأدمن القديم كما كان
    return RedirectResponse("/admin/", status_code=303)

# ── تشغيل الخادم ────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
