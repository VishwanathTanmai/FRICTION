"""
Database models and initialization for Fix My Itch clone.
Uses SQLite for zero-config setup.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixmyitch.db')

CATEGORIES = [
    {'id': 1, 'name': 'Health', 'icon': '🏥', 'color': '#EF4444'},
    {'id': 2, 'name': 'Finance', 'icon': '💰', 'color': '#F59E0B'},
    {'id': 3, 'name': 'Education', 'icon': '📚', 'color': '#3B82F6'},
    {'id': 4, 'name': 'Logistics', 'icon': '📦', 'color': '#8B5CF6'},
    {'id': 5, 'name': 'Food', 'icon': '🍽️', 'color': '#10B981'},
    {'id': 6, 'name': 'Legal', 'icon': '⚖️', 'color': '#6366F1'},
    {'id': 7, 'name': 'Transport', 'icon': '🚗', 'color': '#EC4899'},
    {'id': 8, 'name': 'Housing', 'icon': '🏠', 'color': '#14B8A6'},
    {'id': 9, 'name': 'Agriculture', 'icon': '🌾', 'color': '#84CC16'},
    {'id': 10, 'name': 'Environment', 'icon': '🌍', 'color': '#06B6D4'},
    {'id': 11, 'name': 'Technology', 'icon': '💻', 'color': '#7C3AED'},
    {'id': 12, 'name': 'Employment', 'icon': '💼', 'color': '#F97316'},
    {'id': 13, 'name': 'Safety', 'icon': '🛡️', 'color': '#DC2626'},
    {'id': 14, 'name': 'Governance', 'icon': '🏛️', 'color': '#64748B'},
]


def get_db(db_path=None):
    """Get a database connection with row factory."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path=None):
    """Initialize the database schema."""
    conn = get_db(db_path)
    cursor = conn.cursor()

    # Problems table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            subcategory TEXT,
            frustration_score REAL DEFAULT 0,
            market_size_score REAL DEFAULT 0,
            solvability_score REAL DEFAULT 0,
            overall_score REAL DEFAULT 0,
            root_cause TEXT,
            inefficiency TEXT,
            sentiment REAL DEFAULT 0,
            keyword_tags TEXT,
            source TEXT DEFAULT 'curated',
            source_url TEXT,
            upvotes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            icon TEXT,
            color TEXT,
            problem_count INTEGER DEFAULT 0
        )
    ''')

    # Submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_text TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            email TEXT,
            processed BOOLEAN DEFAULT 0,
            analysis_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            access_key TEXT NOT NULL UNIQUE,
            access_key_verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_category ON problems(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_overall_score ON problems(overall_score DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_frustration ON problems(frustration_score DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_problems_created ON problems(created_at DESC)')

    # Seed categories
    for cat in CATEGORIES:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (id, name, icon, color)
            VALUES (?, ?, ?, ?)
        ''', (cat['id'], cat['name'], cat['icon'], cat['color']))

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {db_path or DB_PATH}")


def insert_problem(conn, problem_data):
    """Insert a single problem into the database."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO problems (
            title, description, category, subcategory,
            frustration_score, market_size_score, solvability_score, overall_score,
            root_cause, inefficiency, sentiment, keyword_tags,
            source, source_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        problem_data.get('title', ''),
        problem_data.get('description', ''),
        problem_data.get('category', 'General'),
        problem_data.get('subcategory', ''),
        problem_data.get('frustration_score', 0),
        problem_data.get('market_size_score', 0),
        problem_data.get('solvability_score', 0),
        problem_data.get('overall_score', 0),
        problem_data.get('root_cause', ''),
        problem_data.get('inefficiency', ''),
        problem_data.get('sentiment', 0),
        json.dumps(problem_data.get('keyword_tags', [])),
        problem_data.get('source', 'curated'),
        problem_data.get('source_url', ''),
    ))
    return cursor.lastrowid


def get_problems(conn, category=None, sort_by='overall_score', order='DESC',
                 limit=20, offset=0, search=None):
    """Fetch problems with optional filters."""
    query = 'SELECT * FROM problems WHERE 1=1'
    params = []

    if category and category != 'All':
        query += ' AND category = ?'
        params.append(category)

    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    allowed_sorts = {
        'overall_score', 'frustration_score', 'market_size_score',
        'solvability_score', 'created_at', 'upvotes'
    }
    if sort_by not in allowed_sorts:
        sort_by = 'overall_score'

    order = 'DESC' if order.upper() == 'DESC' else 'ASC'
    query += f' ORDER BY {sort_by} {order}'
    query += ' LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    cursor = conn.cursor()
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def get_problem_by_id(conn, problem_id):
    """Get a single problem by ID."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM problems WHERE id = ?', (problem_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_random_problems(conn, limit=10):
    """Get random problems for scratch card."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM problems
        ORDER BY RANDOM()
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_top_problems(conn, limit=10):
    """Get top scored problems."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM problems
        ORDER BY overall_score DESC
        LIMIT ?
    ''', (limit,))
    return [dict(row) for row in cursor.fetchall()]


def get_category_stats(conn):
    """Get category statistics."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            c.name, c.icon, c.color,
            COUNT(p.id) as problem_count,
            ROUND(AVG(p.overall_score), 1) as avg_score,
            ROUND(AVG(p.frustration_score), 1) as avg_frustration
        FROM categories c
        LEFT JOIN problems p ON c.name = p.category
        GROUP BY c.name
        ORDER BY problem_count DESC
    ''')
    return [dict(row) for row in cursor.fetchall()]


def get_platform_stats(conn):
    """Get overall platform statistics."""
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM problems')
    total = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(DISTINCT category) as cats FROM problems')
    cats = cursor.fetchone()['cats']

    cursor.execute('SELECT ROUND(AVG(frustration_score), 1) as avg_frust FROM problems')
    avg_frust = cursor.fetchone()['avg_frust'] or 0

    cursor.execute('SELECT ROUND(AVG(overall_score), 1) as avg_score FROM problems')
    avg_score = cursor.fetchone()['avg_score'] or 0

    cursor.execute('''
        SELECT COUNT(*) as today FROM submissions
        WHERE DATE(created_at) = DATE('now')
    ''')
    today = cursor.fetchone()['today']

    return {
        'total_problems': total,
        'categories': cats,
        'avg_frustration': avg_frust,
        'avg_score': avg_score,
        'submissions_today': today
    }


def upvote_problem(conn, problem_id):
    """Increment upvote count for a problem."""
    cursor = conn.cursor()
    cursor.execute('UPDATE problems SET upvotes = upvotes + 1 WHERE id = ?', (problem_id,))
    conn.commit()
    cursor.execute('SELECT upvotes FROM problems WHERE id = ?', (problem_id,))
    row = cursor.fetchone()
    return row['upvotes'] if row else 0


def save_submission(conn, problem_text, category='General', email=None, analysis=None):
    """Save a user-submitted problem."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO submissions (problem_text, category, email, analysis_result)
        VALUES (?, ?, ?, ?)
    ''', (problem_text, category, email, json.dumps(analysis) if analysis else None))
    conn.commit()
    return cursor.lastrowid


def get_total_count(conn, category=None, search=None):
    """Get total problem count for pagination."""
    query = 'SELECT COUNT(*) as total FROM problems WHERE 1=1'
    params = []
    if category and category != 'All':
        query += ' AND category = ?'
        params.append(category)
    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchone()['total']


def create_user(conn, first_name, middle_name, last_name, email, password_hash, access_key):
    """Create a new user."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (first_name, middle_name, last_name, email, password_hash, access_key)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (first_name, middle_name, last_name, email, password_hash, access_key))
    conn.commit()
    return cursor.lastrowid


def get_user_by_email(conn, email):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    return dict(user) if user else None


def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    return dict(user) if user else None


def update_user(conn, user_id, first_name, middle_name, last_name):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET first_name = ?, middle_name = ?, last_name = ?
        WHERE id = ?
    ''', (first_name, middle_name, last_name, user_id))
    conn.commit()


def verify_access_key(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET access_key_verified = 1
        WHERE id = ?
    ''', (user_id,))
    conn.commit()


def update_user_password(conn, user_id, password_hash):
    """Update user password."""
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()


def update_user_access_key(conn, user_id, new_access_key):
    """Update user access key."""
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET access_key = ? WHERE id = ?', (new_access_key, user_id))
    conn.commit()


if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
