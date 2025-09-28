# Festagram - College Event Management System

## Overview

Festagram is a comprehensive college event management platform built with Flask that enables students to discover, register for, and manage college events. The application features role-based access control with separate dashboards for students and administrators, event registration with capacity management and waitlists, real-time notifications, and calendar integration.

Key features include:
- Event browsing and search functionality with category filtering
- Student registration and profile management
- Admin event creation, editing, and monitoring
- Email notifications for event updates
- Calendar view for event visualization
- Registration tracking with capacity limits and waitlist support

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
The application follows a traditional MVC pattern using Flask as the web framework. The codebase is organized into distinct modules:

- **app.py**: Application factory and configuration setup
- **models.py**: SQLAlchemy database models defining the data structure
- **routes.py**: URL routing and request handling logic
- **forms.py**: WTForms for form validation and rendering
- **utils.py**: Utility functions for notifications and email services

### Authentication & Authorization
The system implements Flask-Login for session management with role-based access control. Users are categorized as either 'student' or 'admin' with different permission levels. Password security is handled through Werkzeug's password hashing utilities.

### Database Design
Uses SQLAlchemy ORM with SQLite as the default database (configurable via environment variables). Key entities include:
- **User**: Stores student/admin information with profile data
- **Event**: Contains event details, capacity, and scheduling information
- **EventRegistration**: Manages user event registrations and waitlists
- **Notification**: Handles in-app notifications for users

The database schema supports foreign key relationships and cascading deletes for data integrity.

### Frontend Architecture
Server-side rendered templates using Jinja2 with Bootstrap 5 for responsive design. The frontend includes:
- Dynamic calendar integration using FullCalendar.js
- Real-time UI updates through JavaScript
- Mobile-responsive design with dark theme support
- Form validation and user feedback mechanisms

### Notification System
Dual notification approach combining:
- In-app notifications stored in the database
- Email notifications via Flask-Mail for critical updates
- Event-driven notifications for registration confirmations, waitlist updates, and event changes

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy/Flask-SQLAlchemy**: Database ORM and integration
- **Flask-Login**: User session management
- **WTForms/Flask-WTF**: Form handling and validation
- **Werkzeug**: Password hashing and security utilities

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **FullCalendar.js**: Calendar component for event visualization

### Email Service Integration
- **Flask-Mail**: Email notification system
- **SMTP Configuration**: Configurable email server support (defaults to Gmail SMTP)

### Environment Configuration
The application uses environment variables for:
- Database connection strings (DATABASE_URL)
- Email server credentials (MAIL_USERNAME, MAIL_PASSWORD)
- Session security keys (SESSION_SECRET)
- Mail server configuration (MAIL_SERVER, MAIL_PORT)

### Database Support
- Default: SQLite for development
- Production-ready: Configurable for PostgreSQL or other databases via DATABASE_URL
- Connection pooling and health checks configured for production deployments