"""Database seed script for initial data.

Creates:
- Default super admin account (MUST change password in production)
- Sample departments
- Sample courses
- Sample subjects
- Sample teacher account
- Sample students (without biometric data)

Usage:
    python -m scripts.seed_database
    or
    cd backend && python -c "from scripts.seed_database import seed; seed()"
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database.session import SessionLocal, engine, Base
from app.models import *
from app.core.security import hash_password
from datetime import date, time

def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter(User.username == 'admin').first():
            print('Database already seeded. Skipping.')
            return
        
        print('Seeding database...')
        
        # 1. Create Super Admin
        # WARNING: Change this password immediately in production!
        admin = User(
            username='admin',
            email='admin@attendance.local',
            password_hash=hash_password('Admin@123'),
            full_name='System Administrator',
            role='super_admin',
            is_active=True
        )
        db.add(admin)
        db.flush()
        print(f'  Created super admin: admin / Admin@123')
        print(f'  ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!')
        
        # 2. Create Teacher account
        teacher = User(
            username='teacher1',
            email='teacher@attendance.local',
            password_hash=hash_password('Teacher@123'),
            full_name='Dr. Priya Sharma',
            role='teacher',
            is_active=True
        )
        db.add(teacher)
        db.flush()
        print(f'  Created teacher: teacher1 / Teacher@123')
        
        # 3. Create Departments
        dept_cs = Department(code='CS', name='Computer Science')
        dept_it = Department(code='IT', name='Information Technology')
        dept_ec = Department(code='EC', name='Electronics & Communication')
        db.add_all([dept_cs, dept_it, dept_ec])
        db.flush()
        print(f'  Created 3 departments')
        
        # 4. Create Courses
        mca = Course(code='MCA', name='Master of Computer Applications', department_id=dept_cs.id, duration_years=2)
        btech_cs = Course(code='BTECH-CS', name='B.Tech Computer Science', department_id=dept_cs.id, duration_years=4)
        bca = Course(code='BCA', name='Bachelor of Computer Applications', department_id=dept_cs.id, duration_years=3)
        db.add_all([mca, btech_cs, bca])
        db.flush()
        print(f'  Created 3 courses')
        
        # 5. Create Subjects
        subjects = [
            Subject(code='ML101', name='Machine Learning', course_id=mca.id, department_id=dept_cs.id, semester=3, credits=4, teacher_id=teacher.id),
            Subject(code='AI201', name='Artificial Intelligence', course_id=mca.id, department_id=dept_cs.id, semester=3, credits=4, teacher_id=teacher.id),
            Subject(code='DS301', name='Data Structures', course_id=btech_cs.id, department_id=dept_cs.id, semester=3, credits=3),
            Subject(code='DBMS401', name='Database Management Systems', course_id=btech_cs.id, department_id=dept_cs.id, semester=4, credits=4),
            Subject(code='CN501', name='Computer Networks', course_id=mca.id, department_id=dept_cs.id, semester=2, credits=3, teacher_id=teacher.id),
            Subject(code='SE601', name='Software Engineering', course_id=bca.id, department_id=dept_cs.id, semester=5, credits=3),
        ]
        db.add_all(subjects)
        db.flush()
        print(f'  Created {len(subjects)} subjects')
        
        # 6. Create Sample Students (NO biometric data)
        sample_students = [
            {'student_id': 'MCA001', 'roll_number': '2024MCA001', 'full_name': 'Rahul Sharma', 'email': 'rahul@student.local', 'phone': '9876543210', 'course_id': mca.id, 'department_id': dept_cs.id, 'semester': 3, 'section': 'A'},
            {'student_id': 'MCA002', 'roll_number': '2024MCA002', 'full_name': 'Priya Gupta', 'email': 'priya@student.local', 'phone': '9876543211', 'course_id': mca.id, 'department_id': dept_cs.id, 'semester': 3, 'section': 'A'},
            {'student_id': 'MCA003', 'roll_number': '2024MCA003', 'full_name': 'Aman Verma', 'email': 'aman@student.local', 'phone': '9876543212', 'course_id': mca.id, 'department_id': dept_cs.id, 'semester': 3, 'section': 'A'},
            {'student_id': 'MCA004', 'roll_number': '2024MCA004', 'full_name': 'Sneha Patel', 'email': 'sneha@student.local', 'phone': '9876543213', 'course_id': mca.id, 'department_id': dept_cs.id, 'semester': 3, 'section': 'B'},
            {'student_id': 'MCA005', 'roll_number': '2024MCA005', 'full_name': 'Vikram Singh', 'email': 'vikram@student.local', 'phone': '9876543214', 'course_id': mca.id, 'department_id': dept_cs.id, 'semester': 3, 'section': 'B'},
            {'student_id': 'BT001', 'roll_number': '2024BT001', 'full_name': 'Ananya Desai', 'email': 'ananya@student.local', 'phone': '9876543215', 'course_id': btech_cs.id, 'department_id': dept_cs.id, 'semester': 3, 'section': 'A'},
            {'student_id': 'BT002', 'roll_number': '2024BT002', 'full_name': 'Rohan Mehta', 'email': 'rohan@student.local', 'phone': '9876543216', 'course_id': btech_cs.id, 'department_id': dept_cs.id, 'semester': 3, 'section': 'A'},
            {'student_id': 'BT003', 'roll_number': '2024BT003', 'full_name': 'Kavya Reddy', 'email': 'kavya@student.local', 'phone': '9876543217', 'course_id': btech_cs.id, 'department_id': dept_cs.id, 'semester': 4, 'section': 'A'},
            {'student_id': 'BCA001', 'roll_number': '2024BCA001', 'full_name': 'Arjun Kumar', 'email': 'arjun@student.local', 'phone': '9876543218', 'course_id': bca.id, 'department_id': dept_cs.id, 'semester': 5, 'section': 'A'},
            {'student_id': 'BCA002', 'roll_number': '2024BCA002', 'full_name': 'Divya Nair', 'email': 'divya@student.local', 'phone': '9876543219', 'course_id': bca.id, 'department_id': dept_cs.id, 'semester': 5, 'section': 'A'},
        ]
        
        for s in sample_students:
            # Create student user account
            student_user = User(
                username=s['student_id'].lower(),
                email=s['email'],
                password_hash=hash_password('Student@123'),
                full_name=s['full_name'],
                role='student',
                is_active=True
            )
            db.add(student_user)
            db.flush()
            
            student = Student(
                student_id=s['student_id'],
                roll_number=s['roll_number'],
                full_name=s['full_name'],
                email=s['email'],
                phone=s['phone'],
                course_id=s['course_id'],
                department_id=s['department_id'],
                semester=s['semester'],
                section=s['section'],
                date_of_admission=date(2024, 8, 1),
                status='active',
                user_id=student_user.id
            )
            db.add(student)
        
        db.flush()
        print(f'  Created {len(sample_students)} sample students')
        
        # 7. Create default system settings
        settings = [
            SystemSetting(key='face_recognition_threshold', value='0.6', description='Face recognition distance threshold'),
            SystemSetting(key='low_attendance_threshold', value='75.0', description='Percentage below which attendance is low'),
            SystemSetting(key='late_threshold_minutes', value='15', description='Minutes after session start to mark as late'),
            SystemSetting(key='max_face_samples', value='10', description='Maximum face samples per student'),
            SystemSetting(key='enable_liveness', value='true', description='Enable liveness detection'),
            SystemSetting(key='enable_notifications', value='true', description='Enable notification system'),
            SystemSetting(key='system_name', value='AI Attendance System', description='System display name'),
        ]
        db.add_all(settings)
        
        db.commit()
        print('\n✅ Database seeded successfully!')
        print('\nDefault accounts:')
        print('  Super Admin: admin / Admin@123')
        print('  Teacher: teacher1 / Teacher@123')
        print('  Students: {student_id} / Student@123')
        print('\n⚠️  CHANGE ALL PASSWORDS BEFORE PRODUCTION USE!')
    
    except Exception as e:
        db.rollback()
        print(f'\n❌ Seeding failed: {e}')
        raise
    finally:
        db.close()

if __name__ == '__main__':
    seed()
