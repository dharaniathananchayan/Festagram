from flask_mail import Message
from app import mail, app
from models import Notification, db
import logging

def send_email(subject, recipient, template, **kwargs):
    """Send email notification"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient] if isinstance(recipient, str) else recipient,
            html=template,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        logging.info(f"Email sent to {recipient} with subject: {subject}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {str(e)}")
        return False

def create_notification(user_id, title, message, notification_type, related_event_id=None):
    """Create a new notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_event_id=related_event_id
        )
        db.session.add(notification)
        db.session.commit()
        logging.info(f"Notification created for user {user_id}: {title}")
        return notification
    except Exception as e:
        logging.error(f"Failed to create notification: {str(e)}")
        db.session.rollback()
        return None

def notify_event_update(event, message_type, additional_message=""):
    """Send notifications to all registered users about event updates"""
    from models import EventRegistration, User
    
    registrations = EventRegistration.query.filter_by(event_id=event.id).all()
    
    for registration in registrations:
        user = User.query.get(registration.user_id)
        if user:
            if message_type == 'cancelled':
                title = f"Event Cancelled: {event.title}"
                message = f"Unfortunately, the event '{event.title}' scheduled for {event.start_datetime.strftime('%B %d, %Y at %I:%M %p')} has been cancelled. {additional_message}"
            elif message_type == 'updated':
                title = f"Event Updated: {event.title}"
                message = f"The event '{event.title}' has been updated. Please check the event details for any changes. {additional_message}"
            elif message_type == 'reminder':
                title = f"Event Reminder: {event.title}"
                message = f"This is a reminder that you are registered for '{event.title}' on {event.start_datetime.strftime('%B %d, %Y at %I:%M %p')} at {event.location}."
            else:
                title = f"Event Notification: {event.title}"
                message = additional_message
            
            create_notification(
                user_id=user.id,
                title=title,
                message=message,
                notification_type='event_update',
                related_event_id=event.id
            )

def process_waitlist(event):
    """Process waitlist when spots become available"""
    from models import EventRegistration
    
    available_spots = event.get_available_spots()
    if available_spots <= 0:
        return
    
    waitlisted = EventRegistration.query.filter_by(
        event_id=event.id, 
        status='waitlisted'
    ).order_by(EventRegistration.registration_date).limit(available_spots).all()
    
    for registration in waitlisted:
        registration.status = 'registered'
        event.current_registrations += 1
        
        create_notification(
            user_id=registration.user_id,
            title=f"You're off the waitlist: {event.title}",
            message=f"Great news! A spot has opened up for '{event.title}' and you have been moved from the waitlist to confirmed registration.",
            notification_type='waitlist_promoted',
            related_event_id=event.id
        )
    
    db.session.commit()

def get_category_icon(category):
    """Get Font Awesome icon for event category"""
    icons = {
        'academic': 'fas fa-graduation-cap',
        'cultural': 'fas fa-theater-masks',
        'sports': 'fas fa-running',
        'technical': 'fas fa-code',
        'social': 'fas fa-users',
        'workshop': 'fas fa-tools',
        'seminar': 'fas fa-chalkboard-teacher',
        'competition': 'fas fa-trophy',
        'other': 'fas fa-calendar-alt'
    }
    return icons.get(category, 'fas fa-calendar-alt')

def get_category_color(category):
    """Get Bootstrap color class for event category"""
    colors = {
        'academic': 'primary',
        'cultural': 'info',
        'sports': 'success',
        'technical': 'warning',
        'social': 'secondary',
        'workshop': 'dark',
        'seminar': 'light',
        'competition': 'danger',
        'other': 'secondary'
    }
    return colors.get(category, 'secondary')
