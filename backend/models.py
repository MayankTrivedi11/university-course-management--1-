from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'professor', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Student specific fields
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    major = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    # Professor specific fields
    professor_id = db.Column(db.String(20), unique=True, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=True)
    
    # Relationships
    courses_teaching = db.relationship('Course', backref='instructor', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    grades = db.relationship('Grade', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    credits = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    term = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'completed', 'cancelled'
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    department = db.Column(db.String(100), nullable=False)
    fee = db.Column(db.Float, nullable=False, default=0.0)
    contract_address = db.Column(db.String(100), nullable=True)  # Algorand smart contract address
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    assignments = db.relationship('Assignment', backref='course', lazy=True)
    
    @property
    def instructor_name(self):
        if self.instructor:
            return self.instructor.name
        return "TBA"
    
    @property
    def enrolled_count(self):
        return len(self.enrollments)
    
    @property
    def is_full(self):
        return self.enrolled_count >= self.capacity
    
    def __repr__(self):
        return f'<Course {self.code} - {self.title}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='enrolled')  # 'enrolled', 'completed', 'dropped'
    grade = db.Column(db.String(5), nullable=True)
    transaction_id = db.Column(db.String(100), nullable=True)  # Algorand transaction ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Enrollment: Student {self.student_id} in Course {self.course_id}>'

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)  # percentage weight in course grade
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='assignment', lazy=True)
    grades = db.relationship('Grade', backref='assignment', lazy=True)
    
    def __repr__(self):
        return f'<Assignment {self.title} for Course {self.course_id}>'

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    grade = db.relationship('Grade', backref='submission', lazy=True, uselist=False)
    
    def __repr__(self):
        return f'<Submission by Student {self.student_id} for Assignment {self.assignment_id}>'

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=True)
    score = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Grade for Student {self.student_id} on Assignment {self.assignment_id}: {self.score}>'

