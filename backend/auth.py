from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required as flask_jwt_required, get_jwt_identity as flask_get_jwt_identity
from models import db, User
from functools import wraps
import datetime

auth_bp = Blueprint('auth', __name__)
jwt = JWTManager()

def init_jwt(app):
    jwt.init_app(app)

# Custom decorator for JWT auth
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return flask_jwt_required()(f)(*args, **kwargs)
    return decorated

def get_jwt_identity():
    return flask_get_jwt_identity()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'name', 'role']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"{field} is required"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 409
    
    # Create new user
    new_user = User(
        email=data['email'],
        name=data['name'],
        role=data['role']
    )
    new_user.set_password(data['password'])
    
    # Handle role-specific fields
    if data['role'] == 'student':
        new_user.student_id = data.get('student_id')
        new_user.major = data.get('major')
        new_user.year = data.get('year')
    
    elif data['role'] == 'professor':
        new_user.professor_id = data.get('professor_id')
        new_user.department = data.get('department')
        new_user.title = data.get('title')
    
    db.session.add(new_user)
    
    try:
        db.session.commit()
        # Generate JWT token
        access_token = create_access_token(
            identity=new_user.id,
            expires_delta=datetime.timedelta(days=1)
        )
        
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "role": new_user.role
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Generate JWT token
    access_token = create_access_token(
        identity=user.id,
        expires_delta=datetime.timedelta(days=1)
    )
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    # In a stateless JWT system, the client simply discards the token
    # For added security, we could implement a token blacklist here
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required
def change_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({"error": "Current password and new password required"}), 400
    
    user = User.query.get(current_user_id)
    
    if not user or not user.check_password(data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 401
    
    user.set_password(data['new_password'])
    
    try:
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

