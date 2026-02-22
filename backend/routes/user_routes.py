"""
User Routes - Enhanced with phone+OTP based authentication
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database.db import get_db_connection
import uuid
import random
import hashlib

user_bp = Blueprint('user', __name__)

# In-memory OTP store (use Redis in production)
_otp_store = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


# ─── Registration ─────────────────────────────────────────────────────────────

@user_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """
    Step 1 of sign-up: send OTP to phone number.
    Body: { "phone": "9876543210" }
    OTP is printed to server console (for demo; replace with Twilio in production).
    """
    try:
        data = request.json
        phone = data.get('phone', '').strip()
        if len(phone) < 10:
            return jsonify({'success': False, 'error': 'Valid phone number required'}), 400

        otp = generate_otp()
        _otp_store[phone] = {'otp': otp, 'created_at': datetime.now()}

        print(f"\n{'='*40}")
        print(f"📱 OTP for {phone}: {otp}")
        print(f"{'='*40}\n")

        return jsonify({
            'success': True,
            'message': f'OTP sent to {phone}. Check backend console.',
            'demo_otp': otp  # Include in response for demo convenience
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/register', methods=['POST'])
def register():
    """
    Step 2 of sign-up: register with verified OTP.
    Body: {
        "name": "string",
        "phone": "string",
        "city": "string",
        "emergency_contacts": ["9999999999", "8888888888"],
        "otp": "123456",
        "password": "string" (optional, OTP-based auth)
    }
    """
    try:
        data = request.json
        phone = data.get('phone', '').strip()
        otp = data.get('otp', '').strip()
        name = data.get('name', '').strip()
        city = data.get('city', '').strip()
        emergency_contacts = data.get('emergency_contacts', [])

        if not phone or not otp or not name:
            return jsonify({'success': False, 'error': 'Name, phone and OTP are required'}), 400

        # Verify OTP
        stored = _otp_store.get(phone)
        if not stored or stored['otp'] != otp:
            return jsonify({'success': False, 'error': 'Invalid or expired OTP. Please request a new one.'}), 400

        # Clear used OTP
        del _otp_store[phone]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for existing user
        cursor.execute("SELECT id FROM users WHERE phone = ? OR email = ?", (phone, data.get('email')))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return jsonify({'success': False, 'error': 'Phone number or email already registered. Please login.'}), 409

        user_id = str(uuid.uuid4())
        token = str(uuid.uuid4())

        # Email and password handling
        email = data.get('email', phone + '@safeher.app').strip()
        password = data.get('password')
        hashed_pw = hash_password(password) if password else hash_password(phone)

        # Insert user
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
            'user': {'id': user_id, 'name': name, 'phone': phone, 'city': city}
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """
    Login with phone + OTP.
    Step 1: POST /api/user/send-otp with phone
    Step 2: POST /api/user/login with phone + otp
    """
    try:
        data = request.json
        phone = data.get('phone', '').strip()
        otp = data.get('otp', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        user = None

        # 1. Try Email/Password login
        if email and password:
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hash_password(password)))
            user = cursor.fetchone()
            if not user:
                conn.close()
                return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        # 2. Try OTP login
        elif phone and otp:
            # Verify OTP
            stored = _otp_store.get(phone)
            if not stored or stored['otp'] != otp:
                conn.close()
                return jsonify({'success': False, 'error': 'Invalid OTP. Please request a new one.'}), 400

            del _otp_store[phone]
            cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            user = cursor.fetchone()
            if not user:
                conn.close()
                return jsonify({'success': False, 'error': 'Account not found. Please sign up first.'}), 404
        
        else:
            conn.close()
            return jsonify({'success': False, 'error': 'Email+Password or Phone+OTP required'}), 400

        # Create new session token
        token = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO user_sessions (id, user_id, token, created_at)
            VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), user['id'], token, datetime.now()))
        conn.commit()

        # Get emergency contacts
        cursor.execute("SELECT phone FROM emergency_contacts WHERE user_id = ?", (user['id'],))
        contacts = [row['phone'] for row in cursor.fetchall()]
        conn.close()

        # Get user details
        user_data = dict(user)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_data['id'],
                'name': user_data['name'],
                'phone': user_data['phone'],
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
        cursor.execute("SELECT id, name, phone, city, created_at FROM users WHERE id = ?", (user_id,))
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