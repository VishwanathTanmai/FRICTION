"""
Fix My Itch Clone — Flask Application
A premium problem-discovery platform inspired by Razorpay's Fix My Itch.
Built with Flask, SQLite, Bootstrap 5, and custom NLP.
"""

import os
import json
import secrets
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, g,
    session, redirect, url_for, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import (
    get_db, init_db, get_problems, get_problem_by_id,
    get_random_problems, get_top_problems, get_category_stats,
    get_platform_stats, upvote_problem, save_submission,
    get_total_count, CATEGORIES, DB_PATH,
    create_user, get_user_by_email, get_user_by_id,
    update_user, update_user_password, update_user_access_key,
    verify_access_key
)
from nlp_engine import NLPEngine
from scraper import ProblemScraper

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fixmyitch-secret-key-2024'
app.config['JSON_SORT_KEYS'] = False

# Initialize NLP engine once
nlp = NLPEngine()


@app.before_request
def setup_db_for_vercel():
    """Lazily initialize database for serverless environments."""
    if not os.path.exists(DB_PATH):
        try:
            init_db()
            from seed_data import seed_database
            seed_database(DB_PATH)
        except Exception:
            pass


def get_connection():
    """Get database connection for current request."""
    if 'db' not in g:
        g.db = get_db()
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ─────────────────────────────────────────────
# Auth Decorator
# ─────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

# ─────────────────────────────────────────────
# Page Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    """3D Landing Page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/about')
def about():
    """About Page."""
    return render_template('about.html')

@app.route('/terms')
def terms():
    """Terms and Conditions Page."""
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    """Privacy Policy Page."""
    return render_template('privacy.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Main application dashboard."""
    conn = get_connection()
    top_problems = get_top_problems(conn, limit=6)
    categories = get_category_stats(conn)
    stats = get_platform_stats(conn)
    # Parse keyword_tags JSON for template
    for p in top_problems:
        try:
            p['keyword_tags'] = json.loads(p.get('keyword_tags', '[]'))
        except (json.JSONDecodeError, TypeError):
            p['keyword_tags'] = []
    
    user = get_user_by_id(conn, session['user_id'])
    
    return render_template('index.html',
                           top_problems=top_problems,
                           categories=categories,
                           stats=stats,
                           all_categories=CATEGORIES,
                           user=user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name', '')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
            
        conn = get_connection()
        if get_user_by_email(conn, email):
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))
            
        password_hash = generate_password_hash(password)
        access_key = secrets.token_hex(16)
        
        try:
            create_user(conn, first_name, middle_name, last_name, email, password_hash, access_key)
            flash(f'Signup successful! IMPORTANT: Your access key is {access_key}. Please copy it, you will need it to sign in.', 'success')
            return redirect(url_for('signin'))
        except Exception as e:
            flash(f'Error during signup: {e}', 'danger')
            return redirect(url_for('signup'))
            
    return render_template('auth.html', is_signup=True)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        access_key = request.form.get('access_key')
        
        conn = get_connection()
        user = get_user_by_email(conn, email)
        
        if user and check_password_hash(user['password_hash'], password):
            if not user.get('access_key_verified', 0):
                if user['access_key'] != access_key:
                    flash('Invalid access key for first-time sign-in.', 'danger')
                    return redirect(url_for('signin'))
                else:
                    verify_access_key(conn, user['id'])
            
            session['user_id'] = user['id']
            flash('Successfully signed in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('signin'))
            
    return render_template('auth.html', is_signup=False)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_connection()
    user = get_user_by_id(conn, session['user_id'])
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name', '')
        last_name = request.form.get('last_name')
        update_user(conn, user['id'], first_name, middle_name, last_name)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('profile.html', user=user)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = get_connection()
    user = get_user_by_id(conn, session['user_id'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(user['password_hash'], old_password):
                flash('Incorrect old password.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            else:
                update_user_password(conn, user['id'], generate_password_hash(new_password))
                flash('Password updated successfully.', 'success')
                
        elif action == 'regenerate_key':
            new_key = secrets.token_hex(16)
            update_user_access_key(conn, user['id'], new_key)
            flash(f'New Access Key generated: {new_key}. Please save it immediately.', 'success')
            
        return redirect(url_for('settings'))
        
    return render_template('settings.html', user=user)


# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────

@app.route('/api/problems')
def api_problems():
    """Get paginated problems list with filters."""
    conn = get_connection()
    category = request.args.get('category', 'All')
    sort_by = request.args.get('sort', 'overall_score')
    order = request.args.get('order', 'DESC')
    page = max(1, request.args.get('page', 1, type=int))
    per_page = min(50, request.args.get('per_page', 12, type=int))
    search = request.args.get('search', '').strip()

    offset = (page - 1) * per_page
    problems = get_problems(conn, category=category, sort_by=sort_by,
                            order=order, limit=per_page, offset=offset,
                            search=search if search else None)

    total = get_total_count(conn, category=category if category != 'All' else None,
                            search=search if search else None)

    # Parse keyword_tags
    for p in problems:
        try:
            p['keyword_tags'] = json.loads(p.get('keyword_tags', '[]'))
        except (json.JSONDecodeError, TypeError):
            p['keyword_tags'] = []

    return jsonify({
        'problems': problems,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, -(-total // per_page)),
        'has_next': page * per_page < total,
        'has_prev': page > 1
    })


@app.route('/api/problems/<int:problem_id>')
def api_problem_detail(problem_id):
    """Get single problem detail."""
    conn = get_connection()
    problem = get_problem_by_id(conn, problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    try:
        problem['keyword_tags'] = json.loads(problem.get('keyword_tags', '[]'))
    except (json.JSONDecodeError, TypeError):
        problem['keyword_tags'] = []
    return jsonify(problem)


@app.route('/api/problems/top')
def api_top_problems():
    """Get top scored problems."""
    conn = get_connection()
    limit = min(20, request.args.get('limit', 10, type=int))
    problems = get_top_problems(conn, limit=limit)
    for p in problems:
        try:
            p['keyword_tags'] = json.loads(p.get('keyword_tags', '[]'))
        except (json.JSONDecodeError, TypeError):
            p['keyword_tags'] = []
    return jsonify({'problems': problems})


@app.route('/api/categories')
def api_categories():
    """Get all categories with counts."""
    conn = get_connection()
    categories = get_category_stats(conn)
    return jsonify({'categories': categories})


@app.route('/api/stats')
def api_stats():
    """Get platform statistics."""
    conn = get_connection()
    stats = get_platform_stats(conn)
    return jsonify(stats)


@app.route('/api/scratch_live')
def api_scratch_live():
    """Scrapes Hacker News Ask HN in real-time, NLP analyzes, and returns top 10."""
    try:
        scraper = ProblemScraper()
        # Hacker News Ask HN is a good source for problems
        urls = ["https://news.ycombinator.com/ask"]
        problems = scraper.scrape_and_process(urls, nlp_engine=nlp)
        
        if problems:
            # Sort by overall score descending
            problems.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
            top_10 = problems[:10]
            
            # Ensure proper keys for the frontend
            for p in top_10:
                p['id'] = 'live-' + str(abs(hash(p['title'])))
                p['upvotes'] = 0
            
            return jsonify({'success': True, 'problems': top_10})
        
        # Fallback to database
        conn = get_db(DB_PATH)
        db_problems = [dict(row) for row in get_top_problems(conn, limit=10)]
        return jsonify({'success': True, 'problems': db_problems, 'fallback': True})
        
    except Exception as e:
        print(f"[SCRAPER API ERROR] {e}")
        conn = get_db(DB_PATH)
        db_problems = [dict(row) for row in get_top_problems(conn, limit=10)]
        return jsonify({'success': False, 'error': str(e), 'problems': db_problems, 'fallback': True})


@app.route('/api/scratch-reveal')
def api_scratch_reveal():
    """Get random problems for scratch card."""
    conn = get_db(DB_PATH)
    problems = get_random_problems(conn, limit=10)
    if not problems:
        return jsonify({'error': 'No problems found'}), 404
    for p in problems:
        try:
            p['keyword_tags'] = json.loads(p.get('keyword_tags', '[]'))
        except (json.JSONDecodeError, TypeError):
            p['keyword_tags'] = []
    return jsonify({'success': True, 'problems': problems})


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze a problem text with NLP."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text'].strip()
    if len(text) < 10:
        return jsonify({'error': 'Text too short (min 10 characters)'}), 400

    category = data.get('category', 'General')
    analysis = nlp.analyze_problem(text, category=category)
    return jsonify(analysis)


import smtplib
from email.message import EmailMessage
import threading

def send_email_notification(text, category, user_email):
    """Sends an email notification via Gmail SMTP."""
    try:
        msg = EmailMessage()
        msg.set_content(f"New Problem Submitted!\n\nCategory: {category}\nUser Email: {user_email}\n\nProblem:\n{text}")
        msg['Subject'] = 'New Problem Submitted on Friction'
        msg['From'] = user_email
        msg['To'] = 'vishwanathtanmai003@gmail.com'
        msg['Reply-To'] = user_email

        # MUST SET THESE ENVIRONMENT VARIABLES BEFORE RUNNING THE APP!
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = os.environ.get('SMTP_USER', 'vishwanathtanmai003@gmail.com')
        # App Password provided by user
        smtp_pass = os.environ.get('SMTP_PASS', 'ubtt zvht lphs jqny') 

        if not smtp_pass:
            print("[EMAIL ERROR] Cannot send email. Please set your SMTP_PASS (Google App Password) as an environment variable.")
            return

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            print("[EMAIL SUCCESS] Real-time notification sent to vishwanathtanmai003@gmail.com!")
    except Exception as e:
        print(f"[EMAIL ERROR] Could not send email notification: {e}")

@app.route('/api/submit', methods=['POST'])
def api_submit():
    """Submit a new problem."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text'].strip()
    if len(text) < 20:
        return jsonify({'error': 'Problem statement too short (min 20 characters)'}), 400

    category = data.get('category', 'General')
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Analyze with NLP
    analysis = nlp.analyze_problem(text, category=category)

    conn = get_connection()
    submission_id = save_submission(conn, text, category, email, analysis)

    # Send email notification in the background
    threading.Thread(target=send_email_notification, args=(text, category, email)).start()

    return jsonify({
        'success': True,
        'submission_id': submission_id,
        'analysis': analysis,
        'message': 'Problem submitted and analyzed successfully!'
    })


@app.route('/api/upvote/<int:problem_id>', methods=['POST'])
def api_upvote(problem_id):
    """Upvote a problem."""
    conn = get_connection()
    new_count = upvote_problem(conn, problem_id)
    return jsonify({'upvotes': new_count})


@app.route('/api/problems/search')
def api_search():
    """Search problems with NLP scoring."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'problems': [], 'query': ''})

    conn = get_connection()
    # Basic search
    problems = get_problems(conn, search=query, limit=20)
    for p in problems:
        try:
            p['keyword_tags'] = json.loads(p.get('keyword_tags', '[]'))
        except (json.JSONDecodeError, TypeError):
            p['keyword_tags'] = []

    # Also analyze the search query itself for context
    query_analysis = nlp.analyze_problem(query) if len(query) > 10 else None

    return jsonify({
        'problems': problems,
        'query': query,
        'query_analysis': query_analysis,
        'total': len(problems)
    })


# ─────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return "<h1>404 Not Found</h1><p>The requested URL was not found on the server.</p>", 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return "Something went wrong", 500


# ─────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────

if __name__ == '__main__':
    # Initialize database if not exists
    if not os.path.exists(DB_PATH):
        print("[STARTUP] Initializing database...")
        init_db()
        print("[STARTUP] Seeding problems...")
        try:
            from seed_data import seed_database
            seed_database(DB_PATH)
            print("[STARTUP] Database seeded successfully!")
        except Exception as e:
            print(f"[STARTUP] Seed error: {e}")
            print("[STARTUP] Run 'python seed_data.py' manually to seed.")
    else:
        print(f"[STARTUP] Using existing database at {DB_PATH}")

    print("\n" + "=" * 60)
    print("  Fix My Itch Clone — Starting Server")
    print("  http://127.0.0.1:5000")
    print("=" * 60 + "\n")

    app.run(debug=True, host='127.0.0.1', port=5000)
