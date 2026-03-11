import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, Response
from functools import wraps
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

from models import db
import storage
import auth
import ai_service

load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.secret_key = os.environ.get('SECRET_KEY', 'bug_detection_secret_key_production')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bugdetector.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db.init_app(app)
csrf = CSRFProtect(app)

# Initialize DB on startup
with app.app_context():
    storage.init_db()

# Configure Logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/bugdetector.log', maxBytes=102400, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('BugDetector instance startup')

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500

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
    user = storage.get_user_by_id(session['user_id'])
    history = user.get('history', []) if user else []
    
    total_analyzed = sum(1 for item in history if item.get('type') == 'analysis')
    total_generated = sum(1 for item in history if item.get('type') == 'test_generation')
    
    unique_days = set()
    for item in history:
        if 'created_at' in item:
            unique_days.add(item['created_at'][:10])
            
    streak = 0
    if unique_days:
        try:
            from datetime import datetime, timedelta
            sorted_dates = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in unique_days], reverse=True)
            today = datetime.utcnow().date()
            
            if sorted_dates[0] == today or sorted_dates[0] == (today - timedelta(days=1)):
                streak = 1
                current_date = sorted_dates[0]
                for d in sorted_dates[1:]:
                    if (current_date - d).days == 1:
                        streak += 1
                        current_date = d
                    else:
                        break
        except Exception as e:
            app.logger.error(f"Streak calculation error: {e}")
            streak = len(unique_days)

    stats = {
        'total_analyzed': total_analyzed,
        'total_generated': total_generated,
        'streak': streak,
        'unique_days': list(unique_days)
    }
    
    return render_template('dashboard.html', stats=stats)

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
@csrf.exempt
def analyze_code():
    data = request.get_json()
    code = data.get('code', '')
    user_id = session.get('user_id')

    if not code:
        return jsonify({'error': 'No code provided'}), 400

    def generate():
        full_result = ""
        for chunk in ai_service.analyze_code_snippet(code):
            full_result += chunk
            yield chunk
            
        with app.app_context():
            if user_id:
                storage.save_history(user_id, 'analysis', code, full_result)

    return Response(generate(), mimetype='text/plain')

@app.route('/api/generate_tests', methods=['POST'])
@csrf.exempt
def generate_tests():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    user_id = session.get('user_id')

    if not code:
        return jsonify({'error': 'No code provided'}), 400

    def generate():
        full_result = ""
        for chunk in ai_service.generate_test_cases(code, language):
            full_result += chunk
            yield chunk
            
        with app.app_context():
            if user_id:
                storage.save_history(user_id, 'test_generation', code, full_result)

    return Response(generate(), mimetype='text/plain')

@app.route('/api/increment_score', methods=['POST'])
@csrf.exempt
def increment_score():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    points = data.get('points', 0)
    
    success, new_score = storage.add_score(session['user_id'], points)
    if success:
        return jsonify({'success': True, 'new_score': new_score})
    return jsonify({'error': 'Failed to update score'}), 500

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
