from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
import storage
import auth

# Initialize Flask app
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.secret_key = 'bug_detection_secret_key_123'  # Required for session management

# Initialize DB on startup
storage.init_db()

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Context Processor to make user available in all templates
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = storage.get_user_by_id(session['user_id'])
        return dict(user=user)
    return dict(user=None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = storage.get_user_by_email(email)
        
        if user and auth.verify_password(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate Input
        is_valid, error = auth.validate_signup_input(first_name, last_name, mobile, email, password)
        if not is_valid:
            flash(error, 'danger')
            return render_template('signup.html')
            
        # Hash Password and Create User
        password_hash = auth.hash_password(password)
        success, result = storage.create_user(first_name, last_name, mobile, email, password_hash)
        
        if success:
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result, 'danger') # Error message from storage (e.g. Email exists)
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- Existing Features (Protected) ---

@app.route('/detect')
# @login_required
def detect():
    return render_template('detect.html')

@app.route('/generate')
@login_required
def generate():
    return render_template('generate.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    # API endpoints might need different auth, but for now we'll leave it or protect it
    # If this is called by AJAX from the frontend, session cookie should work.
    # if 'user_id' not in session:
    #     return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    code = data.get('code', '')

    if not code:
        return jsonify({'error': 'No code provided'}), 400

    # Mock Response for now
    mock_result = f"Analysis Report:\n\n1. Syntax Check: OK\n2. Style: PEP8 violations found.\n3. Bug Probability: 15%\n\nSuggested Fix: Add docstrings to your functions.\n\n(Analyzed {len(code)} characters)"
    
    return jsonify({'result': mock_result})

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/donate/success')
def donate_success():
    return render_template('thank_you.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    print("Starting Bug Detection UI...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)
