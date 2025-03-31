from flask import Blueprint, request, jsonify
from models import db, Course, User, Enrollment, Assignment, Submission, Grade
from auth import jwt_required, get_jwt_identity
from smart_contracts import create_course_contract, enroll_student

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/', methods=['GET'])
def get_courses():
    # Query parameters
    term = request.args.get('term')
    year = request.args.get('year')
    department = request.args.get('department')
    status = request.args.get('status', 'active')
    
    # Build query
    query = Course.query
    
    if term:
        query = query.filter_by(term=term)
    if year:
        query = query.filter_by(year=int(year))
    if department:
        query = query.filter_by(department=department)
    if status:
        query = query.filter_by(status=status)
    
    courses = query.all()
    
    result = []
    for course in courses:
        instructor = User.query.get(course.instructor_id) if course.instructor_id else None
        
        result.append({
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "description": course.description,
            "credits": course.credits,
            "term": course.term,
            "year": course.year,
            "department": course.department,
            "instructor": instructor.name if instructor else "TBA",
            "enrolled_count": course.enrolled_count,
            "capacity": course.capacity,
            "status": course.status,
            "fee": course.fee
        })
    
    return jsonify(result)

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    instructor = User.query.get(course.instructor_id) if course.instructor_id else None
    
    # Get assignments
    assignments = []
    for assignment in course.assignments:
        assignments.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date.isoformat(),
            "points": assignment.points,
            "weight": assignment.weight
        })
    
    return jsonify({
        "id": course.id,
        "code": course.code,
        "title": course.title,
        "description": course.description,
        "credits": course.credits,
        "term": course.term,
        "year": course.year,
        "department": course.department,
        "instructor": {
            "id": instructor.id if instructor else None,
            "name": instructor.name if instructor else "TBA",
            "email": instructor.email if instructor else None
        },
        "enrolled_count": course.enrolled_count,
        "capacity": course.capacity,
        "status": course.status,
        "fee": course.fee,
        "assignments": assignments,
        "contract_address": course.contract_address
    })

@courses_bp.route('/', methods=['POST'])
@jwt_required
def create_course():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role not in ['professor', 'admin']:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['code', 'title', 'credits', 'capacity', 'term', 'year', 'department', 'fee']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    # Check if course code already exists
    if Course.query.filter_by(code=data['code']).first():
        return jsonify({"error": "Course code already exists"}), 409
    
    # Create new course
    new_course = Course(
        code=data['code'],
        title=data['title'],
        description=data.get('description', ''),
        credits=data['credits'],
        capacity=data['capacity'],
        term=data['term'],
        year=data['year'],
        department=data['department'],
        fee=data['fee'],
        status='active'
    )
    
    # If created by professor, set instructor to creator
    if user.role == 'professor':
        new_course.instructor_id = user.id
    # If admin and instructor_id provided
    elif data.get('instructor_id'):
        instructor = User.query.get(data['instructor_id'])
        if instructor and instructor.role == 'professor':
            new_course.instructor_id = instructor.id
    
    db.session.add(new_course)
    
    try:
        db.session.commit()
        
        # Create Algorand smart contract for the course
        if data.get('create_contract', True):
            contract_address = create_course_contract(new_course)
            if contract_address:
                new_course.contract_address = contract_address
                db.session.commit()
        
        return jsonify({
            "message": "Course created successfully",
            "course": {
                "id": new_course.id,
                "code": new_course.code,
                "title": new_course.title,
                "contract_address": new_course.contract_address
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required
def update_course(course_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    # Check permissions
    if user.role == 'professor' and course.instructor_id != user.id:
        return jsonify({"error": "Permission denied"}), 403
    elif user.role not in ['professor', 'admin']:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Update fields
    for field in ['title', 'description', 'credits', 'capacity', 'term', 'year', 'department', 'fee', 'status']:
        if field in data:
            setattr(course, field, data[field])
    
    # Admin can change instructor
    if user.role == 'admin' and 'instructor_id' in data:
        instructor = User.query.get(data['instructor_id'])
        if instructor and instructor.role == 'professor':
            course.instructor_id = instructor.id
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Course updated successfully",
            "course": {
                "id": course.id,
                "code": course.code,
                "title": course.title
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required
def enroll_in_course(course_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'student':
        return jsonify({"error": "Only students can enroll in courses"}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    # Check if student is already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=user.id,
        course_id=course.id
    ).first()
    
    if existing_enrollment:
        return jsonify({"error": "Already enrolled in this course"}), 409
    
    # Check if course is full
    if course.is_full:
        return jsonify({"error": "Course is full"}), 400
    
    # Check if course is active
    if course.status != 'active':
        return jsonify({"error": "Course is not active for enrollment"}), 400
    
    # Create enrollment
    new_enrollment = Enrollment(
        student_id=user.id,
        course_id=course.id,
        status='enrolled'
    )
    
    db.session.add(new_enrollment)
    
    try:
        db.session.commit()
        
        # Record enrollment on blockchain if contract exists
        if course.contract_address:
            transaction_id = enroll_student(course.contract_address, user.id, course.id)
            if transaction_id:
                new_enrollment.transaction_id = transaction_id
                db.session.commit()
        
        return jsonify({
            "message": "Successfully enrolled in course",
            "enrollment": {
                "id": new_enrollment.id,
                "course_id": course.id,
                "course_title": course.title,
                "transaction_id": new_enrollment.transaction_id
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@courses_bp.route('/<int:course_id>/assignments', methods=['GET'])
def get_course_assignments(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    result = []
    for assignment in assignments:
        result.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date.isoformat(),
            "points": assignment.points,
            "weight": assignment.weight,
            "created_at": assignment.created_at.isoformat()
        })
    
    return jsonify(result)

@courses_bp.route('/<int:course_id>/assignments', methods=['POST'])
@jwt_required
def create_assignment(course_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    # Check permissions
    if user.role == 'professor' and course.instructor_id != user.id:
        return jsonify({"error": "Permission denied"}), 403
    elif user.role not in ['professor', 'admin']:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'due_date', 'points', 'weight']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    # Create new assignment
    new_assignment = Assignment(
        course_id=course_id,
        title=data['title'],
        description=data.get('description', ''),
        due_date=datetime.datetime.fromisoformat(data['due_date']),
        points=data['points'],
        weight=data['weight']
    )
    
    db.session.add(new_assignment)
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Assignment created successfully",
            "assignment": {
                "id": new_assignment.id,
                "title": new_assignment.title,
                "due_date": new_assignment.due_date.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

