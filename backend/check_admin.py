from models import User
from database import get_session
from werkzeug.security import check_password_hash

session = get_session()
try:
    user = session.query(User).filter_by(username='admin').first()
    if user:
        print(f"User found: {user.username}, Role: {user.role}, Active: {user.is_active}")
        if check_password_hash(user.password_hash, 'admin123'):
            print("Password verification: SUCCESS")
        else:
            print("Password verification: FAILED")
    else:
        print("User 'admin' NOT FOUND")
finally:
    session.close()
