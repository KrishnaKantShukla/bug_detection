from werkzeug.security import generate_password_hash, check_password_hash
import re

def hash_password(password):
    """Hash a password for storage."""
    return generate_password_hash(password)

def verify_password(stored_hash, password):
    """Check a password against its hash."""
    return check_password_hash(stored_hash, password)

def validate_signup_input(first_name, last_name, mobile, email, password):
    """Validate user input for signup."""
    if not all([first_name, last_name, mobile, email, password]):
        return False, "All fields are required"
    
    # Basic email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email address"
    
    # Basic mobile validation (digits only, length check can be added)
    if not mobile.isdigit() or len(mobile) < 10:
        return False, "Invalid mobile number"
        
    return True, ""
