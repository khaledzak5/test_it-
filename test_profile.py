#!/usr/bin/env python3
"""
اختبار وظيفة الملف الشخصي
"""
import requests
import json
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

def test_profile_functionality():
    """اختبار وظائف الملف الشخصي"""
    
    # إنشاء مستخدم اختبار
    db = SessionLocal()
    test_user = db.query(User).filter_by(username='profiletest').first()
    if not test_user:
        test_user = User(
            full_name='اختبار الملف الشخصي',
            username='profiletest',
            password_hash=hash_password('test123'),
            is_admin=False,
            is_hod=False,
            is_college_admin=False,
            is_doc=False
        )
        db.add(test_user)
        db.commit()
        print("✅ تم إنشاء مستخدم اختبار: profiletest / test123")
    else:
        print("✅ مستخدم الاختبار موجود بالفعل")
    
    db.close()
    
    # اختبار تسجيل الدخول
    session = requests.Session()
    login_data = {
        'username': 'profiletest',
        'password': 'test123'
    }
    
    try:
        # تسجيل الدخول
        print("🔄 جاري تسجيل الدخول...")
        response = session.post('http://localhost:8000/auth/login', data=login_data, allow_redirects=False)
        print(f"📊 حالة تسجيل الدخول: {response.status_code}")
        
        if response.status_code in [302, 303]:  # redirect
            print("✅ تم تسجيل الدخول بنجاح")
            
            # اختبار صفحة الملف الشخصي
            print("🔄 جاري فتح صفحة الملف الشخصي...")
            profile_response = session.get('http://localhost:8000/profile/')
            print(f"📊 حالة صفحة الملف الشخصي: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                print("✅ صفحة الملف الشخصي تعمل بنجاح!")
                
                # اختبار تغيير كلمة المرور
                print("🔄 جاري اختبار تغيير كلمة المرور...")
                password_data = {
                    'current_password': 'test123',
                    'new_password': 'newpass123',
                    'confirm_password': 'newpass123'
                }
                
                change_response = session.post('http://localhost:8000/profile/change-password', data=password_data)
                print(f"📊 حالة تغيير كلمة المرور: {change_response.status_code}")
                
                if change_response.status_code == 200:
                    print("✅ تم تغيير كلمة المرور بنجاح!")
                else:
                    print(f"⚠️ فشل تغيير كلمة المرور: {change_response.text[:200]}")
                    
            else:
                print(f"❌ فشل فتح صفحة الملف الشخصي: {profile_response.text[:200]}")
                
        else:
            print(f"❌ فشل تسجيل الدخول: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")

if __name__ == "__main__":
    test_profile_functionality()