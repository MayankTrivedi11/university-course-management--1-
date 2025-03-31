from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from models import db, User, Course, Enrollment, Assignment, Grade
from auth import auth_bp, jwt_required, get_jwt_identity
from courses import courses_bp
from students import students_bp
from professors import professors_bp
from smart_contracts import smart_contracts_bp
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///university.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
app.config['ALGORAND_API_KEY'] = os.environ.get('ALGORAND_API_KEY')
app.config['ALGORAND_APP_ID'] = os.environ.get('ALGORAND_APP_ID')

# Initialize extensions
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(courses_bp, url_prefix='/api/courses')
app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(professors_bp, url_prefix='/api/professors')
app.register_blueprint(smart_contracts_bp, url_prefix='/api/blockchain')

@app.before_first_request
def create_tables():
    db.create_all()
    logger.info("Database tables created")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "University Course Management API is running"})

@app.route('/api/profile', methods=['GET'])
@jwt_required
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "created_at": user.created_at.isoformat()
    })

@app.route('/api/dashboard', methods=['GET'])
@jwt_required
def get_dashboard_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.role == 'student':
        enrollments = Enrollment.query.filter_by(student_id=user.id).all()
        courses = [Course.query.get(e.course_id) for e in enrollments]
        
        course_data = []
        for course in courses:
            if course:
                assignments = Assignment.query.filter_by(course_id=course.id).count()
                completed_assignments = Grade.query.filter_by(
                    student_id=user.id, 
                    assignment_id=Assignment.id
                ).join(Assignment).filter_by(course_id=course.id).count()
                
                progress = 0
                if assignments > 0:
                    progress = (completed_assignments / assignments) * 100
                    
                course_data.append({
                    "id": course.id,
                    "code": course.code,
                    "title": course.title,
                    "instructor": course.instructor_name,
                    "progress": progress,
                    "credits": course.credits
                })
        
        return jsonify({
            "user": {
                "name": user.name,
                "role": user.role
            },
            "courses": course_data,
            "enrollments_count": len(enrollments),
            "total_credits": sum(c.credits for c in courses if c)
        })
    
    elif user.role == 'professor':
        courses = Course.query.filter_by(instructor_id=user.id).all()
        
        course_data = []
        total_students = 0
        
        for course in courses:
            enrollments_count = Enrollment.query.filter_by(course_id=course.id).count()
            total_students += enrollments_count
            
            course_data.append({
                "id": course.id,
                "code": course.code,
                "title": course.title,
                "students_count": enrollments_count,
                "credits": course.credits
            })
            
        return jsonify({
            "user": {
                "name": user.name,
                "role": user.role
            },
            "courses": course_data,
            "courses_count": len(courses),
            "total_students": total_students
        })
    
    else:  # admin
        courses_count = Course.query.count()
        students_count = User.query.filter_by(role='student').count()
        professors_count = User.query.filter_by(role='professor').count()
        enrollments_count = Enrollment.query.count()
        
        return jsonify({
            "user": {
                "name": user.name,
                "role": user.role
            },
            "stats": {
                "courses_count": courses_count,
                "students_count": students_count,
                "professors_count": professors_count,
                "enrollments_count": enrollments_count
            }
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

