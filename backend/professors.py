from flask import Blueprint, request, jsonify
from models import db, User, Course, Enrollment, Assignment, Submission, Grade
from auth import jwt_required, get_jwt_identity
import datetime

professors_bp = Blueprint('professors', __name__)

@professors_bp.route('/', methods=['GET'])
def get_professors():
    # Query parameters
    department = request.args.get('department')
    
    # Build query
    query = User.query.filter_by(role='professor')
    
    if department:
        query = query.filter_by(department=department)
    
    professors = query.all()
    
    result = []
    for professor in professors:
        result.append({
            "id": professor.id,
            "name": professor.name,
            "email": professor.email,
            "professor_id": professor.professor_id,
            "department": professor.department,
            "title": professor.title
        })
    
    return jsonify(result)

@professors_bp.route('/<int:professor_id>', methods=['GET'])
def get_professor(professor_id):
    professor = User.query.filter_by(id=professor_id, role='professor').first()
    
    if not professor:
        return jsonify({"error": "Professor not found"}), 404
    
    # Get professor's courses
    courses = Course.query.filter_by(instructor_id=professor.id).all()
    
    course_data = []
    for course in courses:
        course_data.append({
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "term": course.term,
            "year": course.year,
            "department": course.department,
            "enrolled_count": course.enrolled_count,
            "capacity": course.capacity
        })
    
    return jsonify({
        "id": professor.id,
        "name": professor.name,
        "email": professor.email,
        "professor_id": professor.professor_id,
        "department": professor.department,
        "title": professor.title,
        "courses": course_data
    })

@professors_bp.route('/<int:professor_id>/courses', methods=['GET'])
@jwt_required
def get_professor_courses(professor_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    professor = User.query.filter_by(id=professor_id, role='professor').first()
    if not professor:
        return jsonify({"error": "Professor not found"}), 404
    
    # Professors can only view their own courses
    if current_user.role == 'professor' and current_user.id != professor_id:
        return jsonify({"error": "Permission denied"}), 403
    
    # Query parameters
    term = request.args.get('term')
    year = request.args.get('year')
    status = request.args.get('status')
    
    # Build query
    query = Course.query.filter_by(instructor_id=professor_id)
    
    if term:
        query = query.filter_by(term=term)
    if year:
        query = query.filter_by(year=int(year))
    if status:
        query = query.filter_by(status=status)
    
    courses = query.all()
    
    result = []
    for course in courses:
        result.append({
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "description": course.description,
            "credits": course.credits,
            "term": course.term,
            "year": course.year,
            "department": course.department,
            "enrolled_count": course.enrolled_count,
            "capacity": course.capacity,
            "status": course.status
        })
    
    return jsonify(result)

@professors_bp.route('/<int:professor_id>/assignments/grade', methods=['POST'])
@jwt_required
def grade_assignment(professor_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Professors can only grade their own assignments
    if current_user.role != 'professor' or current_user.id != professor_id:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['submission_id', 'score']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    # Get submission
    submission = Submission.query.get(data['submission_id'])
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    
    # Verify professor teaches this course
    assignment = Assignment.query.get(submission.assignment_id)
    course = Course.query.get(assignment.course_id)
    
    if course.instructor_id != professor_id:
        return jsonify({"error": "You do not teach this course"}), 403
    
    # Check if grade already exists
    existing_grade = Grade.query.filter_by(
        assignment_id=assignment.id,
        student_id=submission.student_id
    ).first()
    
    if existing_grade:
        # Update existing grade
        existing_grade.score = data['score']
        existing_grade.feedback = data.get('feedback', '')
        existing_grade.graded_at = datetime.datetime.utcnow()
        
        try:
            db.session.commit()
            return jsonify({
                "message": "Grade updated successfully",
                "grade": {
                    "id": existing_grade.id,
                    "score": existing_grade.score,
                    "graded_at": existing_grade.graded_at.isoformat()
                }
            })
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    # Create new grade
    new_grade = Grade(
        student_id=submission.student_id,
        assignment_id=assignment.id,
        submission_id=submission.id,
        score=data['score'],
        feedback=data.get('feedback', '')
    )
    
    db.session.add(new_grade)
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Grade created successfully",
            "grade": {
                "id": new_grade.id,
                "score": new_grade.score,
                "graded_at": new_grade.graded_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@professors_bp.route('/<int:professor_id>/courses/<int:course_id>/students', methods=['GET'])
@jwt_required
def get_course_students(professor_id, course_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Professors can only view students in their own courses
    if current_user.role != 'professor' or current_user.id != professor_id:
        return jsonify({"error": "Permission denied"}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    if course.instructor_id != professor_id:
        return jsonify({"error": "You do not teach this course"}), 403
    
    # Get enrollments for this course
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    result = []
    for enrollment in enrollments:
        student = User.query.get(enrollment.student_id)
        
        result.append({
            "student_id": student.id,
            "name": student.name,
            "email": student.email,
            "student_number": student.student_id,
            "major": student.major,
            "year": student.year,
            "enrollment_status": enrollment.status,
            "grade": enrollment.grade
        })
    
    return jsonify(result)

@professors_bp.route('/<int:professor_id>/courses/<int:course_id>/grades', methods=['POST'])
@jwt_required
def submit_final_grades(professor_id, course_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Professors can only submit grades for their own courses
    if current_user.role != 'professor' or current_user.id != professor_id:
        return jsonify({"error": "Permission denied"}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    if course.instructor_id != professor_id:
        return jsonify({"error": "You do not teach this course"}), 403
    
    data = request.get_json()
    
    if not data or 'grades' not in data or not isinstance(data['grades'], list):
        return jsonify({"error": "Invalid grade data format"}), 400
    
    updated_grades = []
    errors = []
    
    for grade_data in data['grades']:
        if 'student_id' not in grade_data or 'grade' not in grade_data:
            errors.append(f"Missing student_id or grade for entry: {grade_data}")
            continue
        
        enrollment = Enrollment.query.filter_by(
            student_id=grade_data['student_id'],
            course_id=course_id
        ).first()
        
        if not enrollment:
            errors.append(f"Student {grade_data['student_id']} not enrolled in this course")
            continue
        
        enrollment.grade = grade_data['grade']
        updated_grades.append({
            "student_id": enrollment.student_id,
            "grade": enrollment.grade
        })
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Final grades submitted successfully",
            "updated_grades": updated_grades,
            "errors": errors
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

