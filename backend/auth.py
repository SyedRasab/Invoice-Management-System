"""
Authentication Module
Handles user login, logout, and session management
"""
import functools
from flask import session, request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, AuditLog
from database import get_session
import json

def hash_password(password):
    """Hash a password for storing"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """Verify a stored password against one provided by user"""
    return check_password_hash(password_hash, password)

def login_required(view):
    """View decorator that requires a logged in user"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({'error': 'Authentication required'}), 401
        return view(**kwargs)
    return wrapped_view

def init_app(app):
    """Initialize auth with app"""
    
    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        g.user = None
        
        if user_id is not None:
             db_session = get_session()
             try:
                 g.user = db_session.query(User).filter_by(id=user_id).first()
             finally:
                 db_session.close()

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
            
        db_session = get_session()
        try:
            user = db_session.query(User).filter_by(username=username).first()
            
            if user and verify_password(user.password_hash, password):
                if not user.is_active:
                    return jsonify({'success': False, 'message': 'Account is disabled'}), 403
                    
                session.clear()
                session['user_id'] = user.id
                session['role'] = user.role
                
                # Log login
                log = AuditLog(
                    user=user.username,
                    action='login',
                    entity_type='user',
                    entity_id=user.id,
                    details=json.dumps({'ip': request.remote_addr})
                )
                db_session.add(log)
                db_session.commit()
                
                return jsonify({
                    'success': True, 
                    'message': 'Login successful',
                    'user': user.to_dict()
                })
            
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            db_session.close()

    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})

    @app.route('/api/auth/check', methods=['GET'])
    def check_auth():
        if g.user:
            return jsonify({
                'authenticated': True, 
                'user': g.user.to_dict()
            })
        return jsonify({'authenticated': False})

    # Initialize default admin if no users exist
    create_default_admin()

def create_default_admin():
    """Create a default admin user if none exists"""
    db_session = get_session()
    try:
        user_count = db_session.query(User).count()
        if user_count == 0:
            print("Creating default admin user...")
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='Admin',
                email='admin@silvertrading.com'
            )
            db_session.add(admin)
            db_session.commit()
            print("Default admin created: admin / admin123")
    except Exception as e:
        print(f"Error creating default admin: {e}")
    finally:
        db_session.close()
