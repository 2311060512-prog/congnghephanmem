
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Tên lớp
    code = db.Column(db.String(20), unique=True, nullable=False)  # Mã lớp
    lecturer_id = db.Column(db.String(50), nullable=True)  # Giảng viên chủ nhiệm
    students = db.relationship('Student', backref='class_info', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='SET NULL'), nullable=True)
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='student', lazy=True, cascade='all, delete-orphan')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, default=3)
    lecturer = db.Column(db.String(50), nullable=True)
    grades = db.relationship('Grade', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='course', lazy=True, cascade='all, delete-orphan')
    classes = db.relationship('Class', secondary='class_course', backref=db.backref('courses', lazy=True))

class ClassCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    semester = db.Column(db.String(20), nullable=False)  # Học kỳ
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Đảm bảo mỗi lớp chỉ học mỗi môn một lần trong một học kỳ
    __table_args__ = (
        db.UniqueConstraint('class_id', 'course_id', 'semester', name='unique_class_course_semester'),
    )

class CourseRegistration(db.Model):
    MaDK = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Mã phiếu đăng ký
    MaTheSV = db.Column(db.String(20), db.ForeignKey('student.student_id'), nullable=False)  # Mã thẻ sinh viên
    MaMH = db.Column(db.String(20), db.ForeignKey('course.code'), nullable=False)  # Mã môn học
    NgayDangKy = db.Column(db.DateTime, default=db.func.current_timestamp())  # Ngày đăng ký
    HocKy = db.Column(db.String(20), nullable=False)  # Học kỳ đăng ký
    TrangThai = db.Column(db.String(20), default='Chưa duyệt')  # Trạng thái đăng ký

    student = db.relationship('Student', backref='course_registrations', lazy=True)
    course = db.relationship('Course', backref='course_registrations', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False, default='123456')
    role = db.Column(db.String(20), nullable=False)  # admin, lecturer, student

    @staticmethod
    def determine_role(username):
        if username.startswith('@'):
            return 'admin'
        elif username.startswith('GV'):
            return 'lecturer'
        elif username.isdigit():
            return 'student'
        return None



class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    enrolled_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='active')  # active, dropped

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    value = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed
    submitted_by = db.Column(db.String(50))  # username of lecturer who submitted
    confirmed_by = db.Column(db.String(50), nullable=True)  # username of admin who confirmed
    submitted_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    confirmed_at = db.Column(db.DateTime, nullable=True)
    note = db.Column(db.String(200), nullable=True)  # Optional note about the grade

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, withdrawn, free
    payment_date = db.Column(db.DateTime, nullable=True)
    note = db.Column(db.String(200), nullable=True)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    author = db.Column(db.String(50))  # username of the creator

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'))
    day_of_week = db.Column(db.Integer)  # 0 = Monday, 6 = Sunday
    start_time = db.Column(db.String(5), nullable=False)    # Format: "HH:MM"
    end_time = db.Column(db.String(5), nullable=False)      # Format: "HH:MM"
    room = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)  # Học kỳ bắt buộc
    active = db.Column(db.Boolean, default=True)  # Whether this schedule is currently active

    # Mỗi lớp chỉ có một lịch học cho mỗi môn trong một học kỳ
    __table_args__ = (
        db.UniqueConstraint('class_id', 'course_id', 'semester', name='unique_class_course_schedule'),
    )

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'))
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)    # Format: "HH:MM"
    duration = db.Column(db.Integer, nullable=False)        # Duration in minutes
    room = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    exam_type = db.Column(db.String(20), nullable=False)   # midterm, final
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Mỗi lớp chỉ có một lịch thi cho mỗi môn trong một học kỳ và loại thi
    __table_args__ = (
        db.UniqueConstraint('class_id', 'course_id', 'semester', 'exam_type', 
                          name='unique_class_course_exam'),
    )

def init_db():
    # Xóa tất cả dữ liệu cũ
    db.drop_all()
    # Tạo lại các bảng mới
    db.create_all()
    
    try:
        # 1. Tạo người dùng mẫu
        users = [
            User(username='@admin', role='admin', password='123456'),
            User(username='GV001', role='lecturer', password='123456'),
            User(username='20230001', role='student', password='123456'),
            User(username='20230002', role='student', password='123456'),
        ]
        db.session.add_all(users)
        db.session.commit()
        
        # 2. Tạo lớp học mẫu
        classes = [
            Class(name='Công nghệ thông tin 1', code='CNTT1', lecturer_id='GV001'),
            Class(name='Công nghệ thông tin 2', code='CNTT2', lecturer_id='GV001'),
        ]
        db.session.add_all(classes)
        db.session.commit()

        # 3. Tạo sinh viên mẫu
        students = [
            Student(student_id='20230001', full_name='Nguyễn Văn A', 
                   dob='2001-01-01', email='20230001@example.com',
                   class_id=classes[0].id),
            Student(student_id='20230002', full_name='Trần Thị B', 
                   dob='2001-02-02', email='20230002@example.com',
                   class_id=classes[1].id),
        ]
        db.session.add_all(students)
        db.session.commit()

        # 4. Tạo môn học mẫu
        courses = [
            Course(code='CSE101', name='Lập trình cơ bản', credits=3, lecturer='GV001'),
            Course(code='MTH101', name='Toán rời rạc', credits=3, lecturer='GV001'),
        ]
        db.session.add_all(courses)
        db.session.commit()

        # 5. Tạo điểm mẫu
        grades = []
        for student in students:
            for course in courses:
                # Điểm đã được xác nhận
                grades.append(
                    Grade(
                        student_id=student.id,
                        course_id=course.id,
                        value=7.5,
                        status='confirmed',
                        submitted_by='GV001',
                        confirmed_by='@admin',
                    )
                )
                # Điểm đang chờ xác nhận
                grades.append(
                    Grade(
                        student_id=student.id,
                        course_id=course.id,
                        value=8.0,
                        status='pending',
                        submitted_by='GV001',
                    )
                )
        db.session.add_all(grades)
        db.session.commit()

        # 6. Tạo học phí mẫu
        payments = [
            Payment(
                student_id=students[0].id,
                amount=80000,
                status='pending',
                note='Học phí học kỳ 1'
            ),
            Payment(
                student_id=students[1].id,
                amount=80000,
                status='paid',
                payment_date=db.func.current_timestamp(),
                note='Học phí học kỳ 1'
            )
        ]
        db.session.add_all(payments)
        db.session.commit()

        # 7. Tạo tin tức mẫu
        news_items = [
            News(
                title='Thông báo khai giảng',
                content='Lễ khai giảng năm học mới sẽ được tổ chức vào ngày 05/09/2025...',
                author='@admin'
            ),
            News(
                title='Lịch thi học kỳ',
                content='Lịch thi học kỳ 1 năm học 2025-2026 đã được cập nhật...',
                author='@admin'
            ),
            News(
                title='Thông báo nghỉ lễ',
                content='Thông báo về lịch nghỉ lễ Quốc khánh 02/09/2025...',
                author='@admin'
            )
        ]
        db.session.add_all(news_items)
        db.session.commit()

        # 8. Liên kết lớp học với môn học
        class_courses = []
        for class_ in classes:
            for course in courses:
                class_courses.append(
                    ClassCourse(
                        class_id=class_.id,
                        course_id=course.id,
                        semester='HK1-2025'
                    )
                )
        db.session.add_all(class_courses)
        db.session.commit()

        # 9. Tạo thời khóa biểu mẫu cho từng lớp
        schedules = []
        days = [0, 2]  # Thứ 2 và thứ 4
        times = [
            ("07:30", "09:00", "A101"),
            ("09:30", "11:00", "A102")
        ]
        
        for class_course in class_courses:
            day, (start, end, room) = days[0], times[0]
            schedules.append(
                Schedule(
                    course_id=class_course.course_id,
                    class_id=class_course.class_id,
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    room=room,
                    semester='HK1-2025'
                )
            )
        
        db.session.add_all(schedules)
        db.session.commit()

        # 10. Tạo lịch thi mẫu
        exams = []
        from datetime import date, timedelta
        exam_date = date(2025, 12, 15)  # Ngày thi 15/12/2025
        
        for class_course in class_courses:
            # Thi giữa kỳ
            exams.append(
                Exam(
                    course_id=class_course.course_id,
                    class_id=class_course.class_id,
                    exam_date=exam_date,
                    start_time='08:00',
                    duration=60,  # 60 phút
                    room='B101',
                    semester='HK1-2025',
                    exam_type='midterm'
                )
            )
            
            # Thi cuối kỳ
            exams.append(
                Exam(
                    course_id=class_course.course_id,
                    class_id=class_course.class_id,
                    exam_date=exam_date + timedelta(days=7),  # 1 tuần sau
                    start_time='08:00',
                    duration=90,  # 90 phút
                    room='B201',
                    semester='HK1-2025',
                    exam_type='final'
                )
            )
            exam_date += timedelta(days=1)  # Mỗi lớp thi cách nhau 1 ngày
        
        db.session.add_all(exams)
        db.session.commit()

        print("Khởi tạo dữ liệu mẫu thành công!")
        
    except Exception as e:
        print(f"Lỗi khi khởi tạo dữ liệu: {str(e)}")
        db.session.rollback()
    

