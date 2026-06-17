from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

db = SQLAlchemy()
Base = declarative_base()

class Volunteer(db.Model):
    __tablename__ = 'volunteer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    city = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    profession = Column(String(100))
    skills = Column(Text)  # comma-separated
    programs_interested = Column(Text)  # comma-separated
    availability_days = Column(Text)
    hours_per_week = Column(Integer)
    mode = Column(Enum('Online', 'Offline', 'Both', name='volunteer_mode'), nullable=False)
    why_volunteer = Column(Text)
    status = Column(Enum('Pending', 'Active', 'Inactive', name='volunteer_status'), default='Pending', nullable=False)
    joined_date = Column(DateTime, default=datetime.utcnow)
    hours_contributed = Column(Integer, default=0)

class Beneficiary(db.Model):
    __tablename__ = 'beneficiary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    city = Column(String(50), nullable=False)
    school_name = Column(String(150))
    program_id = Column(Integer, ForeignKey('program.id'), nullable=False)
    enrollment_date = Column(DateTime, nullable=False)
    status = Column(Enum('Active', 'Completed', 'Dropped', name='beneficiary_status'), default='Active', nullable=False)
    parent_name = Column(String(100))
    parent_phone = Column(String(15))
    performance_score = Column(Integer, nullable=True) # 0-100
    notes = Column(Text)
    
    program = relationship("Program", back_populates="beneficiaries")

class Program(db.Model):
    __tablename__ = 'program'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    target_age_min = Column(Integer)
    target_age_max = Column(Integer)
    capacity = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum('Active', 'Upcoming', 'Completed', name='program_status'), nullable=False)
    city = Column(String(50))

    beneficiaries = relationship("Beneficiary", back_populates="program")

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False) # e.g., 'Volunteer', 'Beneficiary'
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False) # e.g., 'Added', 'Updated', 'Deleted'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text)