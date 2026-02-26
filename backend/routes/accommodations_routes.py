"""
Accommodations Routes - Real Data via OpenStreetMap
Replaces Google Places synthetic data with live OSM hotel data.
"""

from flask import Blueprint, request, jsonify
from services.mapillary_service import search_pois_overpass

accommodations_bp = Blueprint('accommodations', __name__)


@accommodations_bp.route('/search', methods=['GET'])
def search_accommodations():
    """
    Search for real hotels near a location using OpenStreetMap.
    Query params: lat, lng, radius (default 5000m)
    """
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = int(request.args.get('radius', 5000))

        hotels = search_pois_overpass(lat, lng, 'hotel', radius)

        # Enhance hotel data: map stars to rating and ensure distance visibility
        for hotel in hotels:
            # Map OSM stars to rating for UI consistency
            if not hotel.get('rating') and hotel.get('stars'):
                try:
                    hotel['rating'] = float(hotel['stars'])
                except:
                    hotel['rating'] = 0.0
            elif not hotel.get('rating'):
                hotel['rating'] = 0.0

            # Add a simple safety flag based on rating/stars
            stars = hotel.get('stars')
            if stars:
                try:
                    hotel['safety_verified'] = int(float(stars)) >= 3
                except:
                    hotel['safety_verified'] = False
            else:
                # If rating is high, also verify
                rating = hotel.get('rating', 0)
                hotel['safety_verified'] = rating >= 3.0 if rating else None

        return jsonify({
            'success': True,
            'count': len(hotels),
            'accommodations': hotels,
            'source': 'OpenStreetMap (live)',
            'user_location': {'lat': lat, 'lng': lng}
        }), 200

    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Valid lat and lng are required'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@accommodations_bp.route('/safety-tips', methods=['GET'])
def get_accommodation_safety_tips():
    """Get safety tips for choosing accommodations."""
    return jsonify({
        'success': True,
        'safety_tips': {
            'before_booking': [
                'Read recent reviews from solo female travelers',
                'Check the hotel location on the map — prefer well-lit, main roads',
                'Verify 24/7 reception and security availability',
            ],
            'on_arrival': [
                'Check door locks, windows, and peephole',
                'Locate emergency exits',
                'Save reception number',
            ],
            'red_flags': [
                'No visible security or CCTV',
                'Poorly lit entrances or corridors',
                'Isolated location with no nearby establishments',
            ]
        }
    }), 200