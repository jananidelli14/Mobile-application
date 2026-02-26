"""
Safe Her Travel - Backend API
Flask application with all routes and services
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'safeher-secret-key-change-in-production')
app.config['DATABASE'] = 'safeher_travel.db'

# Import routes - FIXED IMPORTS
from routes.user_routes import user_bp
from routes.sos_routes import sos_bp
from routes.location_routes import location_bp
from routes.resources_routes import resources_bp
from routes.chat_routes import chat_bp
from routes.accommodations_routes import accommodations_bp
from routes.community_routes import community_bp
from routes.report_routes import report_bp

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(sos_bp, url_prefix='/api/sos')
app.register_blueprint(location_bp, url_prefix='/api/location')
app.register_blueprint(resources_bp, url_prefix='/api/resources')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(accommodations_bp, url_prefix='/api/accommodations')
app.register_blueprint(community_bp, url_prefix='/api/community')
app.register_blueprint(report_bp, url_prefix='/api/report')

# Health check endpoint
@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'message': 'Safe Her Travel API is running',
        'version': '2.0',
        'status': 'healthy',
        'features': {
            'sos_alerts': True,
            'location_tracking': True,
            'ai_chatbot': True,
            'emergency_resources': True,
            'accommodation_search': True,
            'real_time_data': True
        }
    }), 200

@app.route('/api/health')
def health_check():
    """Detailed health check"""
    import sqlite3
    
    # Check database
    db_healthy = False
    police_count = 0
    hospital_count = 0
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM police_stations")
        police_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM hospitals")
        hospital_count = cursor.fetchone()[0]
        conn.close()
        db_healthy = True
    except Exception as e:
        print(f"Database health check failed: {e}")
    
    # Check AI service
    ai_healthy = bool(os.getenv('GEMINI_API_KEY'))
    
    # Check Google Places
    places_healthy = bool(os.getenv('GOOGLE_PLACES_API_KEY'))
    
    return jsonify({
        'status': 'healthy' if db_healthy else 'degraded',
        'database': {
            'status': 'connected' if db_healthy else 'error',
            'police_stations': f"{police_count} (Cached Fallback)",
            'hospitals': f"{hospital_count} (Cached Fallback)",
            'live_discovery': 'ACTIVE'
        },
        'services': {
            'ai_chatbot': 'ONLINE' if ai_healthy else 'OFFLINE',
            'real_time_tracking': 'ENABLED',
            'mapillary_places': 'CONNECTED' if os.getenv('MAPILLARY_ACCESS_TOKEN') else 'NOT_CONFIGURED',
            'places_discovery': 'Mapillary + OSM (Real-Time)',
            'twilio_sms': 'configured' if os.getenv('TWILIO_ACCOUNT_SID') else 'disabled',
            'sendgrid_email': 'configured' if os.getenv('SENDGRID_API_KEY') else 'disabled'
        }
    }), 200

@app.route('/api/config')
def get_config():
    """Get public configuration for frontend"""
    return jsonify({
        'emergency_numbers': {
            'police': '100',
            'ambulance': '108',
            'national_emergency': '112',
            'women_helpline': '1091',
            'child_helpline': '1098'
        },
        'features': {
            'sos_button': True,
            'live_location_sharing': True,
            'ai_chatbot': True,
            'nearby_resources': True,
            'safe_accommodations': True
        },
        'supported_regions': [
            'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli',
            'Salem', 'Tirunelveli', 'Vellore', 'Thanjavur',
            'Kanyakumari', 'Kodaikanal', 'Ooty', 'Pondicherry'
        ]
    }), 200

@app.route('/api/statistics')
def get_statistics():
    """Get platform statistics"""
    import sqlite3
    
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sos_alerts")
        total_sos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sos_alerts WHERE status = 'resolved'")
        resolved_sos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM police_stations")
        police_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hospitals")
        hospital_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM safe_zones")
        safe_zones_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'statistics': {
                'users': user_count,
                'sos_alerts': {
                    'total': total_sos,
                    'resolved': resolved_sos,
                    'active': total_sos - resolved_sos
                },
                'emergency_resources': {
                    'police_stations': police_count,
                    'hospitals': hospital_count,
                    'safe_zones': safe_zones_count
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'message': 'The request data is invalid or malformed'
    }), 400

if __name__ == '__main__':
    # Start Flask server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("\n" + "="*50)
    print("Safe Her Travel API Server")
    print("="*50)
    print(f"Running on: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print(f"Database: {app.config['DATABASE']}")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )