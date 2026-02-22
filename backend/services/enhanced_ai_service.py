"""
Enhanced AI Service with Real-Time Data Integration
Chatbot powered by Google Gemini with live emergency services data
"""

import os
import sqlite3
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables explicitly from parent directory if needed
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# System prompt
ENHANCED_SYSTEM_PROMPT = """
You are 'SafeHer Assistant', a highly advanced AI safety companion for women traveling in Tamil Nadu, India.
Current Time: {current_time}

Your primary goals:
1. Provide accurate safety advice based on the user's location and nearby resources.
2. If the area has low density of police/hospitals, advise extreme caution.
3. Use a tone that is empowering, calm, and practical.
4. Support multimodal inputs (descriptions of images or voice transcripts).
5. In emergencies, prioritize immediate actions like calling 100 or using the SOS button.

Tamil Nadu Context:
- National Emergency: 112
- Police: 100
- Women Helpline: 1091
"""

model = None
try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        # Try to find a working model
        available_names = []
        try:
            model_list = list(genai.list_models())
            available_names = [m.name for m in model_list]
            print(f"[AI SERVICE] Supported models: {available_names}")
        except Exception as e:
            print(f"[AI SERVICE] ⚠️ Could not list models: {e}. Proceeding with default list.")
            
        # Force use of gemini-2.0-flash
        selected_model = 'models/gemini-2.0-flash'
        print(f"[AI SERVICE] 🚀 Final Selection Force-Set: {selected_model}")
        model = genai.GenerativeModel(selected_model)
    else:
        print("[AI SERVICE] ❌ ERROR: GEMINI_API_KEY is missing!")
except Exception as e:
    print(f"[AI SERVICE] ❌ CRITICAL CONFIG ERROR: {e}")

# Database path
DATABASE_PATH = 'safeher_travel.db'

# Conversation history storage
conversation_histories = {}

def get_real_time_context(user_location: Optional[Dict] = None, place_name: Optional[str] = None) -> str:
    """
    Fetch real-time data from database and OSM to provide context to AI.
    If place_name is provided, it tries to get context for that place.
    """
    try:
        from services.mapillary_service import search_pois_overpass
        
        context_parts = ["🛡️ CURRENT SAFETY CONTEXT:"]
        
        lat, lng = None, None
        if place_name:
            context_parts.append(f"Analyzing safety for: {place_name}")
            # Simplified geocoding for Tamil Nadu (could be expanded)
            cities = {
                'chennai': (13.0827, 80.2707),
                't nagar': (13.0417, 80.2338),
                'egmore': (13.0732, 80.2609),
                'mylapore': (13.0339, 80.2619),
                'adyar': (13.0067, 80.2575),
                'coimbatore': (11.0168, 76.9558),
                'madurai': (9.9252, 78.1198),
                'trichy': (10.7905, 78.7047),
                'salem': (11.6643, 78.1460),
                'vellore': (12.9165, 79.1325),
                'thiruvallur': (13.1439, 79.9132)
            }
            # Basic fuzzy match
            for city, coords in cities.items():
                if city in place_name.lower():
                    lat, lng = coords
                    break
        
        if not lat and user_location:
            lat, lng = user_location['lat'], user_location['lng']
            context_parts.append("Location: User's Current GPS Position")
        elif not lat:
            context_parts.append("User/Target location unknown. Give general safety tips for Tamil Nadu.")
            return "\n".join(context_parts)

        radius_m = 10000
        # Get live data from OSM
        police = search_pois_overpass(lat, lng, 'police', radius_m)
        hospitals = search_pois_overpass(lat, lng, 'hospital', radius_m)
        
        # Analyze safety density
        total_emergency = len(police) + len(hospitals)
        
        if total_emergency == 0:
            context_parts.append(" 🛑 SAFETY WARNING: No police stations or hospitals found within 10km. This area is considered ISOLATED. Advise user to move to a populated area.")
        elif total_emergency < 5:
            context_parts.append(f" ⚠️ CAUTION: Limited emergency services nearby ({total_emergency} resources within 10km).")
        else:
            context_parts.append(f" ✅ SAFETY STATUS: Good coverage. {len(police)} police and {len(hospitals)} hospitals within 10km.")
        
        if police:
            context_parts.append("\nNearest Police Stations:")
            for p in police[:3]:
                context_parts.append(f"- {p['name']} ({p['distance_km']}km away, Phone: {p.get('phone', 'N/A')})")
        
        if hospitals:
            context_parts.append("\nNearest Hospitals:")
            for h in hospitals[:3]:
                context_parts.append(f"- {h['name']} ({h['distance_km']}km away, Phone: {h.get('phone', 'N/A')})")
            
        return "\n".join(context_parts)
    except Exception as e:
        print(f"Error getting context: {e}")
        return "Safety data currently unavailable."

def get_ai_response(user_message: str, conversation_id: str, 
                    user_location: Optional[Dict] = None,
                    image_data: Optional[str] = None,
                    voice_data: Optional[str] = None) -> str:
    """
    Get AI response. Supports multimodal inputs (image/voice as base64).
    """
    try:
        if not model:
            return get_intelligent_fallback_response(user_message, user_location)
        
        if conversation_id not in conversation_histories:
            conversation_histories[conversation_id] = model.start_chat(history=[])
        
        chat = conversation_histories[conversation_id]
        current_time = datetime.now().strftime("%I:%M %p")
        
        # Determine if user is asking about a specific place
        # Simple heuristic: if message starts with "is ... safe" or contains "at ..."
        place_name = None
        if "safe" in user_message.lower() or "visit" in user_message.lower():
            # In a real app, we might use a dedicated entity extraction call
            tokens = user_message.lower().split()
            places_keys = ['t nagar', 'egmore', 'mylapore', 'adyar', 'chennai', 'coimbatore', 'madurai', 'trichy', 'salem', 'vellore']
            for p in places_keys:
                if p in user_message.lower():
                    place_name = p
                    break

        system_prompt = ENHANCED_SYSTEM_PROMPT.format(current_time=current_time)
        real_time_context = get_real_time_context(user_location, place_name)
        
        # Assemble multi-part message for Gemini
        content_parts = [
            f"{system_prompt}\n\n{real_time_context}\n\nUser Message: {user_message}"
        ]
        
        # Handle Image (Base64)
        if image_data:
            import base64
            content_parts.append({
                "mime_type": "image/jpeg",
                "data": image_data
            })
            
        # Note: Voice processing usually requires transcription or direct audio input.
        # For simplicity and multi-modal support, we'll prefix message if voice was used.
        if voice_data:
            content_parts[0] = f"[VOICE INPUT DETECTED] {content_parts[0]}"

        response = chat.send_message(content_parts)
        return response.text
    except Exception as e:
        print(f"AI Service Error during response generation: {e}")
        return f"AI_ERROR: {str(e)}"

def get_intelligent_fallback_response(message: str, user_location: Optional[Dict] = None) -> str:
    message_lower = message.lower()
    if any(word in message_lower for word in ['danger', 'unsafe', 'scared', 'help']):
        return "🚨 Please stay calm. Call 100 or 112 immediately. Move to a well-lit, public place. Use the SOS button in this app to alert your contacts."
    elif 'police' in message_lower:
        return "Emergency Police: 100. Always keep your phone charged and share your location."
    return "I understand your concern. I'm having a slight connectivity issue with my core brain, but I'm still here to help with your safety in Tamil Nadu. Are you in a safe location right now?"

def analyze_safety_threat(message: str) -> Dict:
    message_lower = message.lower()
    if any(word in message_lower for word in ['attack', 'following', 'danger']):
        return {'threat_level': 'high', 'recommended_actions': ['call_police', 'activate_sos']}
    return {'threat_level': 'low', 'recommended_actions': ['stay_alert']}

if __name__ == '__main__':
    # Test
    print(get_ai_response("I'm feeling unsafe", "test_id"))