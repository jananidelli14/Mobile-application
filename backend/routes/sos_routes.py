"""
SOS Emergency Routes
Handles SOS activation, emergency contacts, and alert broadcasting
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from services.notification_service import send_sms, send_email
from services.police_service import alert_nearest_police
from database.db import get_db_connection
import uuid

sos_bp = Blueprint('sos', __name__)

# Active SOS sessions storage (in production, use Redis)
active_sos_sessions = {}

@sos_bp.route('/activate', methods=['POST'])
def activate_sos():
    """
    Activate SOS emergency alert
    Request body: {
        "user_id": "string",
        "location": {"lat": float, "lng": float},
        "emergency_contacts": ["phone1", "phone2"]
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        location = data.get('location')
        emergency_contacts = data.get('emergency_contacts', [])
        
        if not user_id or not location:
            return jsonify({'success': False, 'error': 'Missing user_id or location'}), 400

        # Generate unique SOS session ID
        sos_id = str(uuid.uuid4())
        
        # 1. Alert nearest police stations (Top 5)
        police_stations = alert_nearest_police(location, limit=5)
        
        # Store SOS session
        active_sos_sessions[sos_id] = {
            'user_id': user_id,
            'location': location,
            'status': 'active',
            'activated_at': datetime.now().isoformat(),
            'emergency_contacts': emergency_contacts,
            'police_stations': police_stations
        }
        
        # 2. Alert each police station via simulated SMS
        for station in police_stations:
            police_msg = f"EMERGENCY: User {user_id} activated SOS at {location['lat']},{location['lng']}. Dist: {station['distance_km']}km. ETA: {station['eta_minutes']}min."
            send_sms(station['phone'], police_msg)
        
        # 3. Send SMS to emergency contacts
        for contact in emergency_contacts:
            contact_msg = f"🚨 EMERGENCY ALERT: Your contact has activated SOS! Location: https://maps.google.com/?q={location['lat']},{location['lng']}"
            send_sms(contact, contact_msg)
        
        # 4. Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sos_alerts (id, user_id, latitude, longitude, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sos_id, user_id, location['lat'], location['lng'], 'active', datetime.now()))
        conn.commit()
        conn.close()
        
        # Primary police station is the first one
        primary_police = police_stations[0] if police_stations else {}
        
        return jsonify({
            'success': True,
            'sos_id': sos_id,
            'message': f'SOS activated. Broadcom to {len(police_stations)} police units.',
            'police_station': primary_police,
            'all_police_stations': police_stations,
            'eta_minutes': primary_police.get('eta_minutes', 5),
            'status': 'active'
        }), 200
        
    except Exception as e:
        print(f"SOS Activation ERROR: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sos_bp.route('/status/<sos_id>', methods=['GET'])
def get_sos_status(sos_id):
    """Get current status of SOS alert"""
    if sos_id in active_sos_sessions:
        return jsonify({
            'success': True,
            'sos': active_sos_sessions[sos_id]
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'SOS session not found'
        }), 404

@sos_bp.route('/deactivate/<sos_id>', methods=['POST'])
def deactivate_sos(sos_id):
    """Deactivate SOS alert"""
    try:
        if sos_id in active_sos_sessions:
            active_sos_sessions[sos_id]['status'] = 'resolved'
            active_sos_sessions[sos_id]['resolved_at'] = datetime.now().isoformat()
            
            # Update database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sos_alerts 
                SET status = 'resolved', resolved_at = ?
                WHERE id = ?
            """, (datetime.now(), sos_id))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'SOS deactivated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'SOS session not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@sos_bp.route('/history/<user_id>', methods=['GET'])
def get_sos_history(user_id):
    """Get SOS alert history for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sos_alerts 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))
        
        alerts = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'alerts': [dict(alert) for alert in alerts]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500