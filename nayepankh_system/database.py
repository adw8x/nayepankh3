import os
from datetime import datetime, date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Volunteer, Beneficiary, Program, ActivityLog

# --- Configuration ---
# Create a dummy Flask app to configure SQLAlchemy
app = Flask(__name__)
# Use an in-memory SQLite database for seeding, or a file-based one
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nayepankh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Seeding Logic ---
def seed_database():
    """Creates all tables and seeds them with sample data."""
    with app.app_context():
        # Drop all tables first to start fresh
        db.drop_all()
        # Create all tables defined in models.py
        db.create_all()

        # --- Seed Programs ---
        prog1 = Program(name='Academic Support', category='Education', description='Tutoring for school subjects.', target_age_min=8, target_age_max=16, capacity=50, start_date=date(2023, 1, 1), end_date=date(2023, 12, 31), status='Active', city='Delhi')
        prog2 = Program(name='Digital Literacy', category='Technology', description='Basic computer and internet skills.', target_age_min=12, target_age_max=25, capacity=30, start_date=date(2023, 3, 1), status='Active', city='Mumbai')
        prog3 = Program(name='Career Mentorship', category='Professional Development', description='Guidance from industry professionals.', target_age_min=17, target_age_max=22, capacity=25, start_date=date(2023, 6, 1), status='Upcoming', city='Bangalore')
        
        db.session.add_all([prog1, prog2, prog3])
        db.session.commit()

        # --- Seed Volunteers ---
        vol1 = Volunteer(name='Priya Sharma', email='priya.s@example.com', phone='9876543210', city='Delhi', age=28, gender='Female', profession='Software Engineer', skills='Python, Web Dev', programs_interested='Digital Literacy,Career Mentorship', availability_days='Sat,Sun', hours_per_week=6, mode='Online', why_volunteer='To give back to the community.', status='Active', joined_date=datetime(2023, 2, 15), hours_contributed=50)
        vol2 = Volunteer(name='Rohan Verma', email='rohan.v@example.com', phone='8765432109', city='Mumbai', age=35, gender='Male', profession='Marketing Manager', skills='Communication, SEO', programs_interested='Career Mentorship', availability_days='Wed,Fri', hours_per_week=4, mode='Offline', why_volunteer='Passionate about education.', status='Active', joined_date=datetime(2023, 4, 10), hours_contributed=30)
        vol3 = Volunteer(name='Anjali Singh', email='anjali.s@example.com', phone='7654321098', city='Bangalore', age=22, gender='Female', profession='Student', skills='Graphic Design', programs_interested='Academic Support', availability_days='Mon,Tue,Wed', hours_per_week=8, mode='Both', why_volunteer='To gain experience.', status='Pending', joined_date=datetime(2023, 5, 20))
        vol4 = Volunteer(name='Amit Kumar', email='amit.k@example.com', phone='6543210987', city='Delhi', age=45, gender='Male', profession='Accountant', skills='Math, Finance', programs_interested='Academic Support', availability_days='Sun', hours_per_week=3, mode='Offline', why_volunteer='Help children with their studies.', status='Inactive', joined_date=datetime(2022, 11, 5), hours_contributed=120)
        vol5 = Volunteer(name='Sunita Reddy', email='sunita.r@example.com', phone='9123456789', city='Hyderabad', age=31, gender='Female', profession='Doctor', skills='First Aid, Health', programs_interested='Academic Support', availability_days='Sat', hours_per_week=5, mode='Online', why_volunteer='Believe in the cause.', status='Active', joined_date=datetime(2023, 1, 5), hours_contributed=65)

        db.session.add_all([vol1, vol2, vol3, vol4, vol5])
        db.session.commit()

        # --- Seed Beneficiaries ---
        beneficiaries_data = [
            {'name': 'Aarav Gupta', 'age': 10, 'city': 'Delhi', 'program_id': prog1.id, 'status': 'Active', 'score': 85},
            {'name': 'Isha Jain', 'age': 14, 'city': 'Delhi', 'program_id': prog1.id, 'status': 'Active', 'score': 92},
            {'name': 'Kabir Khan', 'age': 12, 'city': 'Delhi', 'program_id': prog1.id, 'status': 'Completed', 'score': 78},
            {'name': 'Meera Patel', 'age': 16, 'city': 'Mumbai', 'program_id': prog2.id, 'status': 'Active', 'score': 88},
            {'name': 'Nikhil Rao', 'age': 18, 'city': 'Mumbai', 'program_id': prog2.id, 'status': 'Active', 'score': 95},
            {'name': 'Diya Mehta', 'age': 20, 'city': 'Mumbai', 'program_id': prog2.id, 'status': 'Dropped', 'score': 60},
            {'name': 'Riya Kapoor', 'age': 17, 'city': 'Bangalore', 'program_id': prog3.id, 'status': 'Active', 'score': None},
            {'name': 'Siddharth Menon', 'age': 19, 'city': 'Bangalore', 'program_id': prog3.id, 'status': 'Active', 'score': None},
            {'name': 'Aditi Joshi', 'age': 9, 'city': 'Delhi', 'program_id': prog1.id, 'status': 'Active', 'score': 80},
            {'name': 'Vikram Singh', 'age': 15, 'city': 'Mumbai', 'program_id': prog2.id, 'status': 'Completed', 'score': 91},
        ]

        for data in beneficiaries_data:
            ben = Beneficiary(
                name=data['name'], age=data['age'], gender='Male' if len(data['name']) % 2 == 0 else 'Female', city=data['city'],
                school_name=f"{data['city']} Public School", program_id=data['program_id'],
                enrollment_date=datetime(2023, 4, 1), status=data['status'], parent_name=f"Parent of {data['name']}",
                parent_phone='9999999999', performance_score=data['score'], notes='Initial enrollment.'
            )
            db.session.add(ben)
        db.session.commit()

        # --- Seed Activity Logs ---
        logs = [
            ActivityLog(entity_type='Volunteer', entity_id=vol1.id, action='Added', details='Priya Sharma joined.', timestamp=vol1.joined_date),
            ActivityLog(entity_type='Volunteer', entity_id=vol2.id, action='Added', details='Rohan Verma joined.', timestamp=vol2.joined_date),
            ActivityLog(entity_type='Volunteer', entity_id=vol4.id, action='Updated', details='Amit Kumar status changed to Inactive.', timestamp=datetime(2023, 1, 10)),
            ActivityLog(entity_type='Beneficiary', entity_id=1, action='Added', details='Aarav Gupta enrolled in Academic Support.', timestamp=datetime(2023, 4, 1)),
            ActivityLog(entity_type='Beneficiary', entity_id=2, action='Added', details='Isha Jain enrolled in Academic Support.', timestamp=datetime(2023, 4, 2)),
            ActivityLog(entity_type='Beneficiary', entity_id=4, action='Added', details='Meera Patel enrolled in Digital Literacy.', timestamp=datetime(2023, 4, 5)),
            ActivityLog(entity_type='Program', entity_id=prog1.id, action='Updated', details='Program capacity increased.', timestamp=datetime(2023, 2, 1)),
            ActivityLog(entity_type='Beneficiary', entity_id=3, action='Updated', details='Kabir Khan completed the program.', timestamp=datetime(2023, 5, 15)),
            ActivityLog(entity_type='Volunteer', entity_id=vol1.id, action='Updated', details='Priya Sharma contributed 10 hours.', timestamp=datetime(2023, 5, 18)),
            ActivityLog(entity_type='Volunteer', entity_id=vol3.id, action='Added', details='Anjali Singh applied to volunteer.', timestamp=vol3.joined_date),
            ActivityLog(entity_type='Beneficiary', entity_id=6, action='Updated', details='Diya Mehta dropped from the program.', timestamp=datetime(2023, 5, 25)),
            ActivityLog(entity_type='Volunteer', entity_id=vol2.id, action='Updated', details='Rohan Verma updated profile.', timestamp=datetime(2023, 6, 1)),
            ActivityLog(entity_type='Program', entity_id=prog3.id, action='Added', details='Career Mentorship program created.', timestamp=prog3.start_date),
            ActivityLog(entity_type='Beneficiary', entity_id=7, action='Added', details='Riya Kapoor enrolled in Career Mentorship.', timestamp=datetime(2023, 6, 5)),
            ActivityLog(entity_type='Beneficiary', entity_id=8, action='Added', details='Siddharth Menon enrolled in Career Mentorship.', timestamp=datetime(2023, 6, 6)),
            ActivityLog(entity_type='Volunteer', entity_id=vol5.id, action='Added', details='Sunita Reddy joined.', timestamp=vol5.joined_date),
            ActivityLog(entity_type='Beneficiary', entity_id=9, action='Added', details='Aditi Joshi enrolled in Academic Support.', timestamp=datetime(2023, 6, 10)),
            ActivityLog(entity_type='Beneficiary', entity_id=10, action='Updated', details='Vikram Singh completed the program.', timestamp=datetime(2023, 6, 12)),
            ActivityLog(entity_type='Volunteer', entity_id=vol1.id, action='Updated', details='Priya Sharma updated skills.', timestamp=datetime(2023, 6, 15)),
            ActivityLog(entity_type='Program', entity_id=prog2.id, action='Updated', details='Digital Literacy program description updated.', timestamp=datetime(2023, 6, 20)),
        ]
        db.session.add_all(logs)
        db.session.commit()

        print("Database created and seeded successfully!")

if __name__ == '__main__':
    seed_database()