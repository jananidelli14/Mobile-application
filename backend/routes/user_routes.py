"""
User Routes - Email/Password based authentication
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import get_db_connection
import uuid
import hashlib

user_bp = Blueprint('user', __name__)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ─── Registration ─────────────────────────────────────────────────────────────

@user_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    Body: {
        "name": "string",
        "email": "string",
        "password": "string",
        "phone": "string",
        "city": "string",
        "emergency_contacts": ["9999999999", "8888888888"]
    }
    """
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        phone = data.get('phone', '').strip()
        city = data.get('city', '').strip()
        emergency_contacts = data.get('emergency_contacts', [])

        if not email or not password or not name:
            return jsonify({'success': False, 'error': 'Name, email and password are required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for existing user
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return jsonify({'success': False, 'error': 'Email already registered. Please login.'}), 409

        user_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        hashed_pw = hash_password(password)

        health_conditions = data.get('health_conditions', '')
        consent_agreed = data.get('consent_agreed', 0)
        
        cursor.execute("""
            INSERT INTO users (id, name, email, phone, password, city, health_conditions, consent_agreed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, email, phone, hashed_pw, city, health_conditions, consent_agreed, datetime.now()))

        # Save session
        cursor.execute("""
            INSERT OR REPLACE INTO user_sessions (id, user_id, token, created_at)
            VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), user_id, token, datetime.now()))

        # Save emergency contacts
        for contact_phone in emergency_contacts:
            if contact_phone.strip():
                cursor.execute("""
                    INSERT INTO emergency_contacts (id, user_id, name, phone, relationship, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), user_id, 'Emergency Contact', contact_phone.strip(), 'Emergency', datetime.now()))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'user_id': user_id,
            'token': token,
            'user': {'id': user_id, 'name': name, 'email': email, 'phone': phone, 'city': city}
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """
    Login with Email and Password.
    Body: {"email": "...", "password": "..."}
    """
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hash_password(password)))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

        token = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO user_sessions (id, user_id, token, created_at)
            VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), user['id'], token, datetime.now()))
        conn.commit()

        cursor.execute("SELECT phone FROM emergency_contacts WHERE user_id = ?", (user['id'],))
        contacts = [row['phone'] for row in cursor.fetchall()]
        conn.close()

        user_data = dict(user)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_data['id'],
                'name': user_data['name'],
                'email': user_data['email'],
                'phone': user_data.get('phone', ''),
                'city': user_data.get('city', ''),
                'health_conditions': user_data.get('health_conditions', ''),
                'consent_agreed': user_data.get('consent_agreed', 0),
                'emergency_contacts': contacts
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, phone, city, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT phone FROM emergency_contacts WHERE user_id = ?", (user_id,))
        contacts = [row['phone'] for row in cursor.fetchall()]
        conn.close()

        if user:
            return jsonify({'success': True, 'user': {**dict(user), 'emergency_contacts': contacts}}), 200
        return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/emergency-contacts', methods=['POST'])
def add_emergency_contact():
    """Add emergency contact"""
    try:
        data = request.json
        contact_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergency_contacts (id, user_id, name, phone, relationship, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (contact_id, data['user_id'], data['name'], data['phone'], data.get('relationship', 'Emergency Contact'), datetime.now()))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'contact_id': contact_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/emergency-contacts/<user_id>', methods=['GET'])
def get_emergency_contacts(user_id):
    """Get all emergency contacts for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emergency_contacts WHERE user_id = ?", (user_id,))
        contacts = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'contacts': [dict(c) for c in contacts]}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500