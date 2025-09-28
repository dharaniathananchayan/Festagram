from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from models import User, Event, EventRegistration, Notification
from forms import LoginForm, RegistrationForm, ProfileForm, EventForm, SearchForm
from utils import create_notification, notify_event_update, process_waitlist, get_category_icon, get_category_color
from datetime import datetime, timedelta
from sqlalchemy import or_, and_

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        elif current_user.is_organizer():
            return redirect(url_for('organizer_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    # Show upcoming events for anonymous users
    upcoming_events = Event.query.filter(
        Event.start_datetime > datetime.utcnow(),
        Event.is_active == True
    ).order_by(Event.start_datetime).limit(6).all()
    
    return render_template('index.html', events=upcoming_events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            student_id=form.student_id.data,
            phone=form.phone.data,
            department=form.department.data,
            year=form.year.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        create_notification(
            user_id=user.id,
            title="Welcome to Festagram!",
            message="Your account has been created successfully. Start exploring events and register for exciting activities.",
            notification_type='welcome'
        )
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    elif current_user.is_organizer():
        return redirect(url_for('organizer_dashboard'))
    
    # Get user's registered events
    registered_events = db.session.query(Event).join(EventRegistration).filter(
        EventRegistration.user_id == current_user.id,
        EventRegistration.status.in_(['registered', 'waitlisted'])
    ).order_by(Event.start_datetime).all()
    
    # Get upcoming events user can register for
    upcoming_events = Event.query.filter(
        Event.start_datetime > datetime.utcnow(),
        Event.is_active == True,
        ~Event.id.in_([reg.event_id for reg in current_user.registrations])
    ).order_by(Event.start_datetime).limit(6).all()
    
    # Get recent notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('student_dashboard.html', 
                         registered_events=registered_events,
                         upcoming_events=upcoming_events,
                         notifications=notifications)

@app.route('/organizer_dashboard')
@login_required
def organizer_dashboard():
    if not current_user.is_organizer():
        flash('Access denied. Event Organizer privileges required.', 'danger')
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    # Get events created by this organizer
    created_events = Event.query.filter_by(
        created_by=current_user.id
    ).order_by(Event.created_at.desc()).all()
    
    # Get statistics for organizer's events
    total_created = len(created_events)
    total_registrations = sum(event.current_registrations for event in created_events)
    upcoming_events = [event for event in created_events if event.start_datetime > datetime.utcnow() and event.is_active]
    
    # Get recent registrations for organizer's events
    recent_registrations = db.session.query(EventRegistration, Event, User).join(
        Event, EventRegistration.event_id == Event.id
    ).join(
        User, EventRegistration.user_id == User.id
    ).filter(
        Event.created_by == current_user.id
    ).order_by(EventRegistration.registration_date.desc()).limit(10).all()
    
    return render_template('organizer_dashboard.html',
                         created_events=created_events,
                         total_created=total_created,
                         total_registrations=total_registrations,
                         upcoming_events=upcoming_events,
                         recent_registrations=recent_registrations)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        if current_user.is_organizer():
            return redirect(url_for('organizer_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    # Get event statistics
    total_events = Event.query.count()
    active_events = Event.query.filter_by(is_active=True).count()
    upcoming_events = Event.query.filter(
        Event.start_datetime > datetime.utcnow(),
        Event.is_active == True
    ).count()
    
    # Get recent events created by this admin
    recent_events = Event.query.filter_by(
        created_by=current_user.id
    ).order_by(Event.created_at.desc()).limit(5).all()
    
    # Get events needing attention (low registration, approaching deadline)
    attention_events = Event.query.filter(
        Event.start_datetime > datetime.utcnow(),
        Event.is_active == True,
        Event.current_registrations < (Event.capacity * 0.3),
        Event.registration_deadline > datetime.utcnow()
    ).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_events=total_events,
                         active_events=active_events,
                         upcoming_events=upcoming_events,
                         recent_events=recent_events,
                         attention_events=attention_events)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.student_id = form.student_id.data
        current_user.phone = form.phone.data
        current_user.department = form.department.data
        current_user.year = form.year.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.student_id.data = current_user.student_id
        form.phone.data = current_user.phone
        form.department.data = current_user.department
        form.year.data = current_user.year
    return render_template('profile.html', form=form)

@app.route('/events')
def events():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Event.query.filter(Event.is_active == True)
    
    if search:
        query = query.filter(or_(
            Event.title.contains(search),
            Event.description.contains(search),
            Event.location.contains(search)
        ))
    
    if category:
        query = query.filter(Event.category == category)
    
    events = query.order_by(Event.start_datetime).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Add category icons and colors
    for event in events.items:
        event.icon = get_category_icon(event.category)
        event.color = get_category_color(event.category)
    
    return render_template('events.html', events=events, search_form=search_form, 
                         search=search, category=category)

@app.route('/event/<int:id>')
def event_detail(id):
    event = Event.query.get_or_404(id)
    event.icon = get_category_icon(event.category)
    event.color = get_category_color(event.category)
    
    user_registration = None
    if current_user.is_authenticated:
        user_registration = EventRegistration.query.filter_by(
            user_id=current_user.id,
            event_id=event.id
        ).first()
    
    return render_template('event_detail.html', event=event, user_registration=user_registration)

@app.route('/register_event/<int:id>', methods=['POST'])
@login_required
def register_event(id):
    event = Event.query.get_or_404(id)
    
    # Check if user is already registered
    existing_registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=event.id
    ).first()
    
    if existing_registration:
        flash('You are already registered for this event.', 'warning')
        return redirect(url_for('event_detail', id=id))
    
    # Check if registration is still open
    if not event.can_register():
        flash('Registration for this event is closed.', 'danger')
        return redirect(url_for('event_detail', id=id))
    
    # Create registration
    status = 'registered' if not event.is_full() else 'waitlisted'
    registration = EventRegistration(
        user_id=current_user.id,
        event_id=event.id,
        status=status
    )
    
    if status == 'registered':
        event.current_registrations += 1
        flash(f'Successfully registered for {event.title}!', 'success')
        create_notification(
            user_id=current_user.id,
            title=f"Registration Confirmed: {event.title}",
            message=f"You have successfully registered for '{event.title}' on {event.start_datetime.strftime('%B %d, %Y at %I:%M %p')}.",
            notification_type='registration_confirmed',
            related_event_id=event.id
        )
    else:
        flash(f'Event is full. You have been added to the waitlist for {event.title}.', 'info')
        create_notification(
            user_id=current_user.id,
            title=f"Added to Waitlist: {event.title}",
            message=f"The event '{event.title}' is currently full, but you have been added to the waitlist. You will be notified if a spot becomes available.",
            notification_type='waitlist_added',
            related_event_id=event.id
        )
    
    db.session.add(registration)
    db.session.commit()
    
    return redirect(url_for('event_detail', id=id))

@app.route('/cancel_registration/<int:id>', methods=['POST'])
@login_required
def cancel_registration(id):
    event = Event.query.get_or_404(id)
    registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=event.id
    ).first()
    
    if not registration:
        flash('You are not registered for this event.', 'warning')
        return redirect(url_for('event_detail', id=id))
    
    if registration.status == 'registered':
        event.current_registrations -= 1
        # Process waitlist
        process_waitlist(event)
    
    db.session.delete(registration)
    db.session.commit()
    
    flash(f'Registration cancelled for {event.title}.', 'info')
    return redirect(url_for('event_detail', id=id))

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if not (current_user.is_admin() or current_user.is_organizer()):
        flash('Access denied. Admin or Event Organizer privileges required.', 'danger')
        return redirect(url_for('events'))
    
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            location=form.location.data,
            capacity=form.capacity.data,
            registration_deadline=form.registration_deadline.data,
            allow_waitlist=form.allow_waitlist.data,
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash(f'Event "{event.title}" created successfully!', 'success')
        return redirect(url_for('event_detail', id=event.id))
    return render_template('create_event.html', form=form)

@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    
    if not (current_user.is_admin() or current_user.is_organizer()) and event.created_by != current_user.id:
        flash('Access denied. You can only edit events you created.', 'danger')
        return redirect(url_for('event_detail', id=id))
    
    form = EventForm()
    if form.validate_on_submit():
        # Check if significant changes were made
        significant_changes = (
            event.start_datetime != form.start_datetime.data or
            event.end_datetime != form.end_datetime.data or
            event.location != form.location.data
        )
        
        event.title = form.title.data
        event.description = form.description.data
        event.category = form.category.data
        event.start_datetime = form.start_datetime.data
        event.end_datetime = form.end_datetime.data
        event.location = form.location.data
        event.capacity = form.capacity.data
        event.registration_deadline = form.registration_deadline.data
        event.allow_waitlist = form.allow_waitlist.data
        event.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        if significant_changes:
            notify_event_update(event, 'updated', 'Please review the updated event details.')
        
        flash(f'Event "{event.title}" updated successfully!', 'success')
        return redirect(url_for('event_detail', id=event.id))
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.category.data = event.category
        form.start_datetime.data = event.start_datetime
        form.end_datetime.data = event.end_datetime
        form.location.data = event.location
        form.capacity.data = event.capacity
        form.registration_deadline.data = event.registration_deadline
        form.allow_waitlist.data = event.allow_waitlist
    
    return render_template('edit_event.html', form=form, event=event)

@app.route('/delete_event/<int:id>', methods=['POST'])
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    
    if not current_user.is_admin() and event.created_by != current_user.id:
        flash('Access denied. You can only delete events you created.', 'danger')
        return redirect(url_for('event_detail', id=id))
    
    # Notify all registered users
    notify_event_update(event, 'cancelled', 'We apologize for any inconvenience caused.')
    
    event.is_active = False
    db.session.commit()
    
    flash(f'Event "{event.title}" has been cancelled.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/calendar')
def calendar():
    # Get events for calendar view
    events = Event.query.filter(
        Event.is_active == True,
        Event.start_datetime >= datetime.utcnow() - timedelta(days=30)
    ).all()
    
    # Convert events to calendar format
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'url': url_for('event_detail', id=event.id),
            'color': get_category_color(event.category),
            'category': event.category
        })
    
    return render_template('calendar.html', events=calendar_events)

@app.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Mark notifications as read when viewed
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).all()
    
    for notification in unread_notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/event_registrations/<int:event_id>')
@login_required
def event_registrations(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user has permission to view registrations
    if not (current_user.is_admin() or (current_user.is_organizer() and event.created_by == current_user.id)):
        flash('Access denied. You can only view registrations for events you created.', 'danger')
        return redirect(url_for('events'))
    
    # Get all registrations for this event
    registrations = db.session.query(EventRegistration, User).join(
        User, EventRegistration.user_id == User.id
    ).filter(
        EventRegistration.event_id == event_id
    ).order_by(EventRegistration.registration_date.desc()).all()
    
    # Separate by status
    registered_users = [(reg, user) for reg, user in registrations if reg.status == 'registered']
    waitlisted_users = [(reg, user) for reg, user in registrations if reg.status == 'waitlisted']
    
    return render_template('event_registrations.html', 
                         event=event,
                         registered_users=registered_users,
                         waitlisted_users=waitlisted_users)

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        return dict(unread_notifications_count=unread_count)
    return dict(unread_notifications_count=0)

@app.context_processor
def inject_utility_functions():
    return dict(
        get_category_color=get_category_color,
        get_category_icon=get_category_icon
    )

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
