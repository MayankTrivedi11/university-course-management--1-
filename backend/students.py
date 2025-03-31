from flask import Blueprint, request, jsonify
from models import db, User, Course, Enrollment, Assignment, Submission, Grade
from auth import jwt_required, get_jwt_identity

students_bp = Blueprint('students', __name__)

@students_bp.route('/', methods=['GET'])
@jwt_required
def get_students():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role not in ['professor', 'admin']:
        return jsonify({"error": "Permission denied"}), 403
    
    # Query parameters
    major = request.args.get('major')
    year = request.args.get('year')
    
    # Build query
    query = User.query.filter_by(role='student')
    
    if major:
        query = query.filter_by(major=major)
    if year:
        query = query.filter_by(year=int(year))
    
    students = query.all()
    
    result = []
    for student in students:
        result.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "student_id": student.student_id,
            "major": student.major,
            "year": student.year
        })
    
    return jsonify(result)

@students_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required
def get_student(student_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Students can only view their own profile
    if current_user.role == 'student' and current_user.id != student_id:
        return jsonify({"error": "Permission denied"}), 403
    
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Get student's enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    courses = []
    
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        instructor = User.query.get(course.instructor_id) if course.instructor_id else None
        
        courses.append({
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "term": course.term,
            "year": course.year,
            "instructor": instructor.name if instructor else "TBA",
            "status": enrollment.status,
            "grade": enrollment.grade
        })
    
    return jsonify({
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "student_id": student.student_id,
        "major": student.major,
        "year": student.year,
        "courses": courses
    })

@students_bp.route('/<int:student_id>/courses', methods=['GET'])
@jwt_required
def get_student_courses(student_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Students can only view their own courses
    if current_user.role == 'student' and current_user.id != student_id:
        return jsonify({"error": "Permission denied"}), 403
    
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Query parameters
    term = request.args.get('term')
    year = request.args.get('year')
    status = request.args.get('status')
    
    # Get student's enrollments
    query = Enrollment.query.filter_by(student_id=student.id)
    
    if status:
        query = query.filter_by(status=status)
    
    enrollments = query.all()
    result = []
    
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        
        # Apply term/year filters
        if term and course.term != term:
            continue
        if year and course.year != int(year):
            continue
        
        instructor = User.query.get(course.instructor_id) if course.instructor_id else None
        
        result.append({
            "enrollment_id": enrollment.id,
            "enrollment_status": enrollment.status,
            "enrollment_grade": enrollment.grade,
            "course": {
                "id": course.id,
                "code": course.code,
                "title": course.title,
                "description": course.description,
                "credits": course.credits,
                "term": course.term,
                "year": course.year,
                "instructor": instructor.name if instructor else "TBA"
            }
        })
    
    return jsonify(result)

@students_bp.route('/<int:student_id>/assignments', methods=['GET'])
@jwt_required
def get_student_assignments(student_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Students can only view their own assignments
    if current_user.role == 'student' and current_user.id != student_id:
        return jsonify({"error": "Permission denied"}), 403
    
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Get student's enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    course_ids = [e.course_id for e in enrollments]
    
    # Get assignments for these courses
    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
    
    result = []
    for assignment in assignments:
        course = Course.query.get(assignment.course_id)
        
        # Check if student has submitted
        submission = Submission.query.filter_by(
            assignment_id=assignment.id,
            student_id=student.id
        ).first()
        
        # Check if assignment has been graded
        grade = Grade.query.filter_by(
            assignment_id=assignment.id,
            student_id=student.id
        ).first()
        
        result.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date.isoformat(),
            "points": assignment.points,
            "weight": assignment.weight,
            "course": {
                "id": course.id,
                "code": course.code,
                "title": course.title
            },
            "submission_status": "Submitted" if submission else "Not Submitted",
            "submitted_at": submission.submitted_at.isoformat() if submission else None,
            "grade": grade.score if grade else None,
            "feedback": grade.feedback if grade else None
        })
    
    return jsonify(result)

@students_bp.route('/<int:student_id>/submissions', methods=['POST'])
@jwt_required
def submit_assignment(student_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Students can only submit their own assignments
    if current_user.role != 'student' or current_user.id != student_id:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    if not data or 'assignment_id' not in data:
        return jsonify({"error": "Assignment ID is required"}), 400
    
    assignment = Assignment.query.get(data['assignment_id'])
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Check if student is enrolled in the course
    enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=assignment.course_id
    ).first()
    
    if not enrollment:
        return jsonify({"error": "Not enrolled in this course"}), 403
    
    # Check if assignment is already submitted
    existing_submission = Submission.query.filter_by(
        assignment_id=assignment.id,
        student_id=student_id
    ).first()
    
    if existing_submission:
        return jsonify({"error": "Assignment already submitted"}), 409
    
    # Create submission
    new_submission = Submission(
        assignment_id=assignment.id,
        student_id=student_id,
        content=data.get('content', ''),
        file_path=data.get('file_path')
    )
    
    db.session.add(new_submission)
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Assignment submitted successfully",
            "submission": {
                "id": new_submission.id,
                "assignment_id": new_submission.assignment_id,
                "submitted_at": new_submission.submitted_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@students_bp.route('/<int:student_id>/grades', methods=['GET'])
@jwt_required
def get_student_grades(student_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Students can only view their own grades
    if current_user.role == 'student' and current_user.id != student_id:
        return jsonify({"error": "Permission denied"}), 403
    
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Get student's enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    
    result = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        
        # Get assignments for this course
        assignments = Assignment.query.filter_by(course_id=course.id).all()
        
        assignment_grades = []
        total_points = 0
        earned_points = 0
        
        for assignment in assignments:
            grade = Grade.query.filter_by(
                assignment_id=assignment.id,
                student_id=student.id
            ).first()
            
            total_points += assignment.points * assignment.weight
            if grade:
                earned_points += grade.score * assignment.weight
            
            assignment_grades.append({
                "assignment_id": assignment.id,
                "title": assignment.title,
                "due_date": assignment.due_date.isoformat(),
                "points": assignment.points,
                "weight": assignment.weight,
                "score": grade.score if grade else None,
                "feedback": grade.feedback if grade else None
            })
        
        # Calculate course grade
        course_grade = None
        if total_points > 0:
            percentage = (earned_points / total_points) * 100
            course_grade = get_letter_grade(percentage)
        
        result.append({
            "course": {
                "id": course.id,
                "code": course.code,
                "title": course.title,
                "term": course.term,
                "year": course.year
            },
            "final_grade": enrollment.grade or course_grade,
            "assignments": assignment_grades
        })
    
    return jsonify(result)

def get_letter_grade(percentage):
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"

