"""
Community Routes - Tourist Experience Sharing
Allows users to share and read travel experiences.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from database.db import get_db_connection

community_bp = Blueprint('community', __name__)


@community_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get community posts, with optional category filter."""
    try:
        category = request.args.get('category')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT * FROM community_posts 
                WHERE category = ? 
                ORDER BY created_at DESC LIMIT 50
            """, (category,))
        else:
            cursor.execute("""
                SELECT * FROM community_posts ORDER BY created_at DESC LIMIT 50
            """)
            
        rows = cursor.fetchall()
        conn.close()
        posts = [dict(row) for row in rows]
        return jsonify({'success': True, 'posts': posts}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@community_bp.route('/posts', methods=['POST'])
def create_post():
    """Create a new community post."""
    try:
        data = request.json
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        location_name = data.get('location_name', '').strip()
        user_id = data.get('user_id', 'anonymous')
        user_name = data.get('user_name', 'Traveler')
        category = data.get('category', 'experience')

        if not title or not content:
            return jsonify({'success': False, 'error': 'Title and content are required'}), 400

        post_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO community_posts (id, user_id, user_name, title, content, location_name, category, likes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (post_id, user_id, user_name, title, content, location_name, category, datetime.now()))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'post_id': post_id, 'message': 'Post created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@community_bp.route('/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like a post."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE community_posts SET likes = likes + 1 WHERE id = ?", (post_id,))
        conn.commit()
        cursor.execute("SELECT likes FROM community_posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        return jsonify({'success': True, 'likes': row['likes']}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
