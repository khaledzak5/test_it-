from fastapi.templating import Jinja2Templates
# إضافة الاستيراد الناقص لـ APIRouter
from fastapi import APIRouter
from fastapi import Request
from fastapi import Form, Depends
from fastapi.responses import RedirectResponse
# app/routers/auth.py
from ..database import get_db
from sqlalchemy.orm import Session
from ..models import User, LoginLog
templates = Jinja2Templates(directory="app/templates")
from urllib.parse import urlparse
from ..security import verify_password
from starlette import status

router = APIRouter(prefix="/auth", tags=["Auth"])
templates = Jinja2Templates(directory="app/templates")

# تغيير كلمة المرور عند أول دخول
@router.get("/change-password")
def change_password_form(request: Request):
    u = request.session.get("user")
    if not u:
        return RedirectResponse("/auth/login", status_code=303)
    return templates.TemplateResponse("auth/change_password.html", {"request": request, "error": None})

@router.post("/change-password")
def change_password_submit(request: Request, new_password: str = Form(...), db: Session = Depends(get_db)):
    u = request.session.get("user")
    if not u:
        return RedirectResponse("/auth/login", status_code=303)
    user = db.query(User).filter(User.id == u["id"]).first()
    if not user:
        return RedirectResponse("/auth/login", status_code=303)
    if not new_password or len(new_password) < 6:
        return templates.TemplateResponse("auth/change_password.html", {"request": request, "error": "كلمة المرور يجب أن تكون 6 أحرف على الأقل."})
    from ..security import hash_password
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()
    # بعد تغيير كلمة المرور، وجه المستخدم للصفحة الرئيسية
    return RedirectResponse("/", status_code=303)


def _safe_next(next_url: str | None) -> str | None:
    """
    يسمح فقط بالمسارات المحلية مثل /hod/... أو /admin/...
    ويتجاهل أي روابط خارجية لحماية الـ open redirect.
    """
    if not next_url:
        return None
    parsed = urlparse(next_url)
    # نسمح فقط بمسار داخلي بدون scheme/netloc
    if parsed.scheme or parsed.netloc:
        return None
    if not parsed.path.startswith("/"):
        return None
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


@router.get("/login")
def login_form(request: Request):
    u = request.session.get("user")
    if u:
        # أعِد استخدام نفس منطق الجذر
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str | None = Form(default=None),  # ملتقِط next القادم من الفورم (إن وجد)
    db: Session = Depends(get_db),
):
    user: User | None = db.query(User).filter(User.username == username).first()

    if not user or not user.is_active or not verify_password(password, user.password_hash):
        next_url = _safe_next(next)
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "بيانات الدخول غير صحيحة",
                "next": next_url,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # إذا كان يجب تغيير كلمة المرور، وجه المستخدم لصفحة تغيير كلمة المرور
    if getattr(user, "must_change_password", False):
        request.session["user"] = {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "is_admin": bool(user.is_admin),
            "is_college_admin": bool(getattr(user, "is_college_admin", False)),
            "college_admin_college": getattr(user, "college_admin_college", None),
            "is_hod": bool(user.is_hod),
            "is_doc": bool(getattr(user, "is_doc", False)),
            "hod_college": user.hod_college,
        }
        # تسجيل الدخول في السجل
        ip_address = request.client.host if request.client else None
        login_log = LoginLog(user_id=user.id, username=user.username, ip_address=ip_address)
        db.add(login_log)
        db.commit()
        return RedirectResponse("/auth/change-password", status_code=303)

    # خزّن بيانات قليلة ومفيدة في الجلسة (booleans صريحة)
    request.session["user"] = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "is_admin": bool(user.is_admin),
        "is_college_admin": bool(getattr(user, "is_college_admin", False)),
        "college_admin_college": getattr(user, "college_admin_college", None),
        "is_hod": bool(user.is_hod),
        "is_doc": bool(getattr(user, "is_doc", False)),  # 👈 جديد: طبيب الكلية
        "hod_college": user.hod_college,
    }

    # تسجيل الدخول في السجل
    ip_address = request.client.host if request.client else None
    login_log = LoginLog(user_id=user.id, username=user.username, ip_address=ip_address)
    db.add(login_log)
    db.commit()

    # أولوية التوجيه:
    # 1) next إن وُجد وكان آمنًا
    # 2) لو طبيب → /clinic/
    # 3) لو هود → /hod/
    # 4) لو أدمن كلية → /admin/ (صفحة أدمن الكلية الأصلية)
    # 5) لو أدمن → /admin/
    # 6) غير ذلك → /
    next_url = _safe_next(next)
    if next_url:
        dest = next_url
    elif bool(getattr(user, "is_doc", False)):
        dest = "/clinic/"
    elif bool(user.is_hod):
        dest = "/hod/"
    elif bool(getattr(user, "is_college_admin", False)):
        dest = "/admin/"
    elif bool(user.is_admin):
        dest = "/admin/"
    else:
        dest = "/"

    return RedirectResponse(url=dest, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
