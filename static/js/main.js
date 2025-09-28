// Main JavaScript file for Festagram

// Utility functions
const utils = {
    // Format date for display
    formatDate: (date) => {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },

    // Format relative time
    formatRelativeTime: (date) => {
        const now = new Date();
        const eventDate = new Date(date);
        const diffInHours = (eventDate - now) / (1000 * 60 * 60);

        if (diffInHours < 24 && diffInHours > 0) {
            return `in ${Math.ceil(diffInHours)} hour${Math.ceil(diffInHours) !== 1 ? 's' : ''}`;
        } else if (diffInHours >= 24) {
            const diffInDays = Math.ceil(diffInHours / 24);
            return `in ${diffInDays} day${diffInDays !== 1 ? 's' : ''}`;
        } else {
            return 'Past event';
        }
    },

    // Show loading state
    showLoading: (element) => {
        element.classList.add('loading');
        element.style.position = 'relative';
    },

    // Hide loading state
    hideLoading: (element) => {
        element.classList.remove('loading');
    },

    // Show toast notification
    showToast: (message, type = 'info') => {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        const toast = createToast(message, type);
        toastContainer.appendChild(toast);
        
        // Initialize Bootstrap toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Debounce function for search
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1080';
    document.body.appendChild(container);
    return container;
}

// Create toast element
function createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-${getToastIcon(type)} me-2 text-${type}"></i>
            <strong class="me-auto">Festagram</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    return toast;
}

// Get icon for toast type
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Enhanced form handling
class FormHandler {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (this.form) {
            this.init();
        }
    }

    init() {
        // Add form validation
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Add real-time validation
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateField.bind(this));
            input.addEventListener('input', this.clearFieldError.bind(this));
        });
    }

    handleSubmit(e) {
        if (!this.validateForm()) {
            e.preventDefault();
            utils.showToast('Please fix the errors in the form', 'danger');
            return false;
        }
        
        // Show loading state
        const submitBtn = this.form.querySelector('[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            const originalText = submitBtn.textContent;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            // Reset button after 10 seconds (fallback)
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 10000);
        }
    }

    validateForm() {
        let isValid = true;
        const inputs = this.form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!this.validateField({ target: input })) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    validateField(e) {
        const field = e.target;
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        
        // Clear previous errors
        this.clearFieldError(e);
        
        // Check required fields
        if (isRequired && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.showFieldError(field, 'Please enter a valid email address');
                return false;
            }
        }
        
        // Password validation
        if (field.type === 'password' && value && field.name === 'password') {
            if (value.length < 6) {
                this.showFieldError(field, 'Password must be at least 6 characters long');
                return false;
            }
        }
        
        // Password confirmation
        if (field.name === 'password2' && value) {
            const password = this.form.querySelector('input[name="password"]');
            if (password && value !== password.value) {
                this.showFieldError(field, 'Passwords do not match');
                return false;
            }
        }
        
        return true;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let feedback = field.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    }

    clearFieldError(e) {
        const field = e.target;
        field.classList.remove('is-invalid');
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }
}

// Search functionality
class SearchHandler {
    constructor() {
        this.searchInput = document.querySelector('input[name="search"]');
        this.categorySelect = document.querySelector('select[name="category"]');
        this.resultsContainer = document.querySelector('.events-grid, .search-results');
        
        if (this.searchInput) {
            this.init();
        }
    }

    init() {
        // Debounced search
        const debouncedSearch = utils.debounce(this.performSearch.bind(this), 300);
        
        if (this.searchInput) {
            this.searchInput.addEventListener('input', debouncedSearch);
        }
        
        if (this.categorySelect) {
            this.categorySelect.addEventListener('change', this.performSearch.bind(this));
        }
    }

    performSearch() {
        const searchTerm = this.searchInput?.value.trim() || '';
        const category = this.categorySelect?.value || '';
        
        // Update URL without page reload
        const url = new URL(window.location);
        
        if (searchTerm) {
            url.searchParams.set('search', searchTerm);
        } else {
            url.searchParams.delete('search');
        }
        
        if (category) {
            url.searchParams.set('category', category);
        } else {
            url.searchParams.delete('category');
        }
        
        // Remove page parameter when searching
        url.searchParams.delete('page');
        
        window.history.replaceState({}, '', url);
        
        // Show loading state
        if (this.resultsContainer) {
            utils.showLoading(this.resultsContainer);
        }
        
        // In a real implementation, you would make an AJAX request here
        // For now, we'll just reload the page with new parameters
        setTimeout(() => {
            window.location.href = url.toString();
        }, 300);
    }
}

// Dashboard enhancements
class DashboardHandler {
    constructor() {
        this.init();
    }

    init() {
        this.addCardAnimations();
        this.addCounterAnimations();
        this.addRelativeTimestamps();
    }

    addCardAnimations() {
        const cards = document.querySelectorAll('.card');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                }
            });
        });

        cards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }

    addCounterAnimations() {
        const counters = document.querySelectorAll('[data-count]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.count);
            const duration = 1000;
            const step = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                counter.textContent = Math.floor(current);
            }, 16);
        });
    }

    addRelativeTimestamps() {
        const timestamps = document.querySelectorAll('[data-timestamp]');
        
        timestamps.forEach(timestamp => {
            const date = timestamp.dataset.timestamp;
            const relative = utils.formatRelativeTime(date);
            
            const relativeSpan = document.createElement('span');
            relativeSpan.className = 'text-muted small';
            relativeSpan.textContent = ` (${relative})`;
            timestamp.appendChild(relativeSpan);
        });
    }
}

// Event registration handler
class EventRegistrationHandler {
    constructor() {
        this.init();
    }

    init() {
        // Handle registration forms
        const registrationForms = document.querySelectorAll('form[action*="register_event"], form[action*="cancel_registration"]');
        
        registrationForms.forEach(form => {
            form.addEventListener('submit', this.handleRegistration.bind(this));
        });
    }

    handleRegistration(e) {
        const form = e.target;
        const isCancel = form.action.includes('cancel_registration');
        
        if (isCancel) {
            const confirmMessage = 'Are you sure you want to cancel your registration for this event?';
            if (!confirm(confirmMessage)) {
                e.preventDefault();
                return false;
            }
        }
        
        // Show loading state
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn) {
            utils.showLoading(submitBtn.parentElement);
            submitBtn.disabled = true;
        }
    }
}

// Notification handler
class NotificationHandler {
    constructor() {
        this.init();
    }

    init() {
        this.markNotificationsAsRead();
        this.addNotificationAnimations();
    }

    markNotificationsAsRead() {
        // Mark notifications as read when they come into view
        const unreadNotifications = document.querySelectorAll('.border-primary');
        
        if (unreadNotifications.length === 0) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Simulate marking as read
                    setTimeout(() => {
                        entry.target.classList.remove('border-primary');
                        const badge = entry.target.querySelector('.badge.bg-primary');
                        if (badge) {
                            badge.style.opacity = '0';
                            setTimeout(() => badge.remove(), 300);
                        }
                    }, 1000);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        unreadNotifications.forEach(notification => {
            observer.observe(notification);
        });
    }

    addNotificationAnimations() {
        const notifications = document.querySelectorAll('.notification-item, .list-group-item');
        
        notifications.forEach((notification, index) => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(-20px)';
            notification.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            
            setTimeout(() => {
                notification.style.opacity = '1';
                notification.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }
}

// Responsive utilities
class ResponsiveHandler {
    constructor() {
        this.init();
    }

    init() {
        this.handleMobileNavigation();
        this.handleResponsiveTables();
        window.addEventListener('resize', utils.debounce(this.handleResize.bind(this), 250));
    }

    handleMobileNavigation() {
        // Collapse navbar when clicking on nav links (mobile)
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                }
            });
        });
    }

    handleResponsiveTables() {
        const tables = document.querySelectorAll('.table');
        
        tables.forEach(table => {
            if (!table.parentElement.classList.contains('table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    }

    handleResize() {
        // Trigger custom resize events for components that need them
        window.dispatchEvent(new CustomEvent('responsiveResize', {
            detail: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        }));
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form handlers
    new FormHandler('form');
    
    // Initialize search functionality
    new SearchHandler();
    
    // Initialize dashboard enhancements
    new DashboardHandler();
    
    // Initialize event registration handling
    new EventRegistrationHandler();
    
    // Initialize notification handling
    new NotificationHandler();
    
    // Initialize responsive utilities
    new ResponsiveHandler();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (alert.querySelector('.btn-close')) {
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }, 5000);
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    console.log('🎉 Festagram initialized successfully!');
});

// Export utilities for global use
window.FestagramUtils = utils;
