import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService {
  /// ============================================================
  /// BASE URL CONFIGURATION (Team Safe + Production Ready)
  /// ============================================================
  ///
  /// Priority Order:
  /// 1️⃣ If --dart-define=API_URL is provided → use that
  /// 2️⃣ Else:
  ///      - Android Emulator → http://10.0.2.2:5000/api
  ///      - iOS Simulator → http://localhost:5000/api
  ///
  /// For Production (Render):
  /// flutter run --dart-define=API_URL=https://yourapp.onrender.com/api
  /// ============================================================

  static String get baseUrl {
    const envUrl = String.fromEnvironment('API_URL');
    if (envUrl.isNotEmpty) return envUrl;

    if (kIsWeb) {
      return 'http://localhost:5000/api';
    }

    if (Platform.isAndroid) {
      return 'http://10.0.2.2:5000/api';
    } else {
      return 'http://localhost:5000/api';
    }
  }

  /// ───────────────────────────────────────────────────────────
  /// AUTH
  /// ───────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String phone,
    required String city,
    required List<String> emergencyContacts,
    required String password,
    String? healthConditions,
    bool consentAgreed = false,
  }) async {
    return _post('/user/register', {
      'name': name,
      'email': email,
      'phone': phone,
      'password': password,
      'city': city,
      'emergency_contacts': emergencyContacts,
      'health_conditions': healthConditions,
      'consent_agreed': consentAgreed ? 1 : 0,
    });
  }

  Future<Map<String, dynamic>> loginWithEmail({
    required String email,
    required String password,
  }) async {
    return _post('/user/login', {'email': email, 'password': password});
  }

  /// ───────────────────────────────────────────────────────────
  /// SOS
  /// ───────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> activateSOS({
    required String userId,
    required double lat,
    required double lng,
    required List<String> emergencyContacts,
  }) async {
    return _post('/sos/activate', {
      'user_id': userId,
      'location': {'lat': lat, 'lng': lng},
      'emergency_contacts': emergencyContacts,
    });
  }

  /// ───────────────────────────────────────────────────────────
  /// CHAT
  /// ───────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> sendMessage({
    required String userId,
    required String message,
    String? conversationId,
    Map<String, double>? location,
    String? imageBase64,
    String? voiceBase64,
  }) async {
    return _post('/chat/message', {
      'user_id': userId,
      'message': message,
      if (conversationId != null) 'conversation_id': conversationId,
      if (location != null) 'user_location': location,
      if (imageBase64 != null) 'image': imageBase64,
      if (voiceBase64 != null) 'voice': voiceBase64,
    });
  }

  /// ───────────────────────────────────────────────────────────
  /// REPORT
  /// ───────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> submitReport({
    required String userId,
    required String type,
    required String description,
    required double lat,
    required double lng,
  }) async {
    return _post('/report/submit', {
      'user_id': userId,
      'type': type,
      'description': description,
      'location': {'lat': lat, 'lng': lng},
    });
  }

  /// ───────────────────────────────────────────────────────────
  /// RESOURCES
  /// ───────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getNearbyPolice(double lat, double lng,
      {int radius = 10000}) async {
    return _get(
        '/resources/police-stations?lat=$lat&lng=$lng&radius=$radius');
  }

  Future<Map<String, dynamic>> getNearbyHospitals(double lat, double lng,
      {int radius = 10000}) async {
    return _get(
        '/resources/hospitals?lat=$lat&lng=$lng&radius=$radius');
  }

  Future<Map<String, dynamic>> getNearbyHotels(double lat, double lng) async {
    return _get(
        '/accommodations/search?lat=$lat&lng=$lng&female_friendly=true');
  }

  /// ───────────────────────────────────────────────────────────
  /// COMMUNITY
  /// ───────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getCommunityPosts() async {
    return _get('/community/posts');
  }

  Future<Map<String, dynamic>> createCommunityPost({
    required String userId,
    required String userName,
    required String title,
    required String content,
    required String locationName,
    String category = 'experience',
  }) async {
    return _post('/community/posts', {
      'user_id': userId,
      'user_name': userName,
      'title': title,
      'content': content,
      'location_name': locationName,
      'category': category,
    });
  }

  Future<Map<String, dynamic>> likePost(String postId) async {
    return _post('/community/posts/$postId/like', {});
  }

  /// ============================================================
  /// INTERNAL HELPERS
  /// ============================================================

  Future<Map<String, dynamic>> _get(String endpoint) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl$endpoint'));
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> _post(
      String endpoint, Map<String, dynamic> body) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }
}