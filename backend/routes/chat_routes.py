"""
Chat Routes
AI-powered chatbot for safety assistance - FIXED IMPORTS
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from services.enhanced_ai_service import get_ai_response
from database.db import get_db_connection
import uuid

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/debug', methods=['GET'])
def ai_debug():
    from services import enhanced_ai_service
    import os
    return jsonify({
        'imported_file': enhanced_ai_service.__file__,
        'model_configured': enhanced_ai_service.model is not None,
        'api_key_present': enhanced_ai_service.GEMINI_API_KEY is not None,
        'model_name': str(enhanced_ai_service.model) if enhanced_ai_service.model else 'None',
        'env_port': os.getenv('PORT', '5001')
    })

@chat_bp.route('/message', methods=['POST'])
def send_message():
    """
    Send message to AI chatbot
    Request body: {
        "user_id": "string",
        "message": "string",
        "conversation_id": "string",
        "user_location": {"lat": float, "lng": float},
        "image": "base64_string",
        "voice": "base64_string"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        user_location = data.get('user_location')
        image_data = data.get('image')
        voice_data = data.get('voice')
        
        # Save user message
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (id, conversation_id, user_id, message, sender, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), conversation_id, user_id, message, 'user', datetime.now()))
        conn.commit()
        
        # Get AI response with multimodal context
        ai_response = get_ai_response(
            message, 
            conversation_id, 
            user_location,
            image_data=image_data,
            voice_data=voice_data
        )
        
        # Save AI response
        cursor.execute("""
            INSERT INTO chat_messages (id, conversation_id, user_id, message, sender, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), conversation_id, user_id, ai_response, 'assistant', datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Chat Route Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get entire conversation history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'messages': [dict(msg) for msg in messages]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/safety-tips', methods=['GET'])
def get_safety_tips():
    """Get AI-generated safety tips"""
    tips = [
        {
            "id": 1,
            "title": "Share Your Location",
            "description": "Always share your live location with trusted contacts when traveling",
            "category": "prevention"
        },
        {
            "id": 2,
            "title": "Trust Your Instincts",
            "description": "If a situation feels unsafe, remove yourself immediately",
            "category": "awareness"
        },
        {
            "id": 3,
            "title": "Keep Phone Charged",
            "description": "Ensure your phone is always charged when traveling",
            "category": "preparation"
        },
        {
            "id": 4,
            "title": "Avoid Isolated Areas",
            "description": "Stay in well-lit, populated areas especially at night",
            "category": "prevention"
        },
        {
            "id": 5,
            "title": "Use Verified Transport",
            "description": "Only use registered and verified transportation services",
            "category": "transport"
        }
    ]
    
    return jsonify({
        'success': True,
        'tips': tips
    }), 200