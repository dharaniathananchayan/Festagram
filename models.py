from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'admin', or 'organizer'
    department = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='user', lazy=True, cascade='all, delete-orphan')
    created_events = db.relationship('Event', foreign_keys='Event.created_by', backref='creator', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_organizer(self):
        return self.role == 'organizer'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # academic, cultural, sports, etc.
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_registrations = db.Column(db.Integer, default=0)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    allow_waitlist = db.Column(db.Boolean, default=True)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def is_full(self):
        return self.current_registrations >= self.capacity
    
    def get_available_spots(self):
        return max(0, self.capacity - self.current_registrations)
    
    def get_waitlist_count(self):
        return EventRegistration.query.filter_by(event_id=self.id, status='waitlisted').count()
    
    def can_register(self):
        return datetime.utcnow() <= self.registration_deadline and self.is_active
    
    def __repr__(self):
        return f'<Event {self.title}>'

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='registered')  # 'registered', 'waitlisted', 'cancelled'
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event'),)
    
    def __repr__(self):
        return f'<EventRegistration User:{self.user_id} Event:{self.event_id} Status:{self.status}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'event_update', 'registration_confirmed', 'waitlist_promoted', etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    
    # Relationship
    related_event = db.relationship('Event', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'
