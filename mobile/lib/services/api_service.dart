import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://localhost:5000/api',
  );

  // ─── Auth ──────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> sendOtp(String phone) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/user/send-otp'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'phone': phone}),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String phone,
    required String city,
    required List<String> emergencyContacts,
    required String otp,
    String? healthConditions,
    bool consentAgreed = false,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/user/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          'email': email,
          'phone': phone,
          'city': city,
          'emergency_contacts': emergencyContacts,
          'otp': otp,
          'health_conditions': healthConditions,
          'consent_agreed': consentAgreed ? 1 : 0,
        }),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> login({
    required String phone,
    required String otp,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/user/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'phone': phone, 'otp': otp}),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> loginWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/user/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // ─── SOS ───────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> activateSOS({
    required String userId,
    required double lat,
    required double lng,
    required List<String> emergencyContacts,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/sos/activate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'location': {'lat': lat, 'lng': lng},
          'emergency_contacts': emergencyContacts,
        }),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // ─── Chat ──────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> sendMessage({
    required String userId,
    required String message,
    String? conversationId,
    Map<String, double>? location,
    String? imageBase64,
    String? voiceBase64,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat/message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'message': message,
          if (conversationId != null) 'conversation_id': conversationId,
          if (location != null) 'user_location': location,
          if (imageBase64 != null) 'image': imageBase64,
          if (voiceBase64 != null) 'voice': voiceBase64,
        }),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // ─── Reporting ─────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> submitReport({
    required String userId,
    required String type,
    required String description,
    required double lat,
    required double lng,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/report/submit'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'type': type,
          'description': description,
          'location': {'lat': lat, 'lng': lng},
        }),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // ─── Resources ─────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getNearbyPolice(double lat, double lng,
      {int radius = 10000}) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$baseUrl/resources/police-stations?lat=$lat&lng=$lng&radius=$radius'),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> getNearbyHospitals(double lat, double lng,
      {int radius = 10000}) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$baseUrl/resources/hospitals?lat=$lat&lng=$lng&radius=$radius'),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> getNearbyHotels(double lat, double lng) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$baseUrl/accommodations/search?lat=$lat&lng=$lng&female_friendly=true'),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // ─── Community ─────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getCommunityPosts() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/community/posts'));
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> createCommunityPost({
    required String userId,
    required String userName,
    required String title,
    required String content,
    required String locationName,
    String category = 'experience',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/community/posts'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'user_name': userName,
          'title': title,
          'content': content,
          'location_name': locationName,
          'category': category,
        }),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> likePost(String postId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/community/posts/$postId/like'),
        headers: {'Content-Type': 'application/json'},
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }
}
