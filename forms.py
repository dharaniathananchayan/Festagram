from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, IntegerField, DateTimeField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from wtforms.widgets import DateTimeLocalInput
from models import User, Event
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('organizer', 'Event Organizer')
    ], validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[Length(max=20)])
    phone = StringField('Phone Number', validators=[Length(max=15)])
    department = StringField('Department', validators=[Length(max=100)])
    year = IntegerField('Year of Study', validators=[NumberRange(min=1, max=6)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')
    
    def validate_student_id(self, student_id):
        if student_id.data:
            user = User.query.filter_by(student_id=student_id.data).first()
            if user:
                raise ValidationError('This student ID is already registered.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    student_id = StringField('Student ID', validators=[Length(max=20)])
    phone = StringField('Phone Number', validators=[Length(max=15)])
    department = StringField('Department', validators=[Length(max=100)])
    year = IntegerField('Year of Study', validators=[NumberRange(min=1, max=6)])
    submit = SubmitField('Update Profile')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()], render_kw={"rows": 4})
    category = SelectField('Category', choices=[
        ('academic', 'Academic'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('technical', 'Technical'),
        ('social', 'Social'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('competition', 'Competition'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    start_datetime = DateTimeField('Start Date & Time', 
                                 widget=DateTimeLocalInput(),
                                 validators=[DataRequired()],
                                 format='%Y-%m-%dT%H:%M')
    end_datetime = DateTimeField('End Date & Time', 
                               widget=DateTimeLocalInput(),
                               validators=[DataRequired()],
                               format='%Y-%m-%dT%H:%M')
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1, max=10000)])
    registration_deadline = DateTimeField('Registration Deadline', 
                                        widget=DateTimeLocalInput(),
                                        validators=[DataRequired()],
                                        format='%Y-%m-%dT%H:%M')
    allow_waitlist = BooleanField('Allow Waitlist')
    submit = SubmitField('Create Event')
    
    def validate_end_datetime(self, end_datetime):
        if end_datetime.data <= self.start_datetime.data:
            raise ValidationError('End time must be after start time.')
    
    def validate_registration_deadline(self, registration_deadline):
        if registration_deadline.data >= self.start_datetime.data:
            raise ValidationError('Registration deadline must be before event start time.')
        if registration_deadline.data <= datetime.now():
            raise ValidationError('Registration deadline must be in the future.')

class SearchForm(FlaskForm):
    search = StringField('Search Events', validators=[Length(max=100)])
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('academic', 'Academic'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('technical', 'Technical'),
        ('social', 'Social'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('competition', 'Competition'),
        ('other', 'Other')
    ])
    submit = SubmitField('Search')
