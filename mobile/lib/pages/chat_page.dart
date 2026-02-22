import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';
import 'package:geolocator/geolocator.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final ApiService _apiService = ApiService();
  final LocationService _locationService = LocationService();
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  Position? _pos;
  String? _conversationId;

  final List<Map<String, dynamic>> _messages = [
    {
      'role': 'assistant',
      'text': "Hello! 🙏 I'm SafeHer AI, your Tamil Nadu safety companion.\n\nI can help you with:\n• 🚨 Emergency guidance\n• 📍 Nearest police & hospitals\n• 🛡️ Safety tips\n• 🏨 Safe hotel recommendations\n\nHow can I help keep you safe today?"
    }
  ];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _getLocation();
  }

  Future<void> _getLocation() async {
    final pos = await _locationService.getCurrentLocation();
    if (mounted) setState(() => _pos = pos);
  }

  String? _selectedImageBase64;
  String? _selectedVoiceBase64;

  void _sendMessage() async {
    if ((_controller.text.trim().isEmpty && _selectedImageBase64 == null && _selectedVoiceBase64 == null) || _isLoading) return;
    final userMsg = _controller.text.trim();
    final image = _selectedImageBase64;
    final voice = _selectedVoiceBase64;

    setState(() {
      _messages.add({
        'role': 'user', 
        'text': voice != null ? "🎤 Voice Message: $userMsg" : (image != null ? "📸 Image Message: $userMsg" : userMsg),
        'hasImage': image != null,
      });
      _isLoading = true;
      _selectedImageBase64 = null;
      _selectedVoiceBase64 = null;
    });
    _controller.clear();
    _scrollToBottom();

    final response = await _apiService.sendMessage(
      userId: 'flutter_user_001',
      message: userMsg,
      conversationId: _conversationId,
      location: _pos != null ? {'lat': _pos!.latitude, 'lng': _pos!.longitude} : null,
      imageBase64: image,
      voiceBase64: voice,
    );
/* ... rest of the method logic unchanged ... */
    if (mounted) {
      setState(() {
        _isLoading = false;
        _conversationId = response['conversation_id'];
        _messages.add({
          'role': 'assistant',
          'text': response['success'] == true
              ? (response['response'] ?? "I'm having trouble responding. Call 112 for emergencies.")
              : "Connection issue. For emergencies: Call 100 (Police) or 112.",
        });
      });
      _scrollToBottom();
    }
  }

  void _mockImageSelection() {
    setState(() {
      _selectedImageBase64 = "base64_image_data";
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("📸 Image attached (Mocked)")));
    });
  }

  void _mockVoiceRecording() {
    setState(() {
      _selectedVoiceBase64 = "base64_voice_data";
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("🎤 Voice recorded (Mocked)")));
    });
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(2),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFF5D3891).withOpacity(0.1), width: 2),
              ),
              child: const CircleAvatar(
                backgroundColor: Color(0xFFF5F5F7),
                radius: 18,
                child: Icon(Icons.auto_awesome_rounded, color: Color(0xFF5D3891), size: 18),
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("SafeHer AI", style: TextStyle(color: Color(0xFF1F1F1F), fontWeight: FontWeight.w900, fontSize: 17, letterSpacing: -0.5)),
                Row(
                  children: [
                    Container(width: 6, height: 6, decoration: const BoxDecoration(color: Color(0xFF00ADB5), shape: BoxShape.circle)),
                    const SizedBox(width: 6),
                    const Text("Always Active", style: TextStyle(color: Color(0xFF8E8E93), fontSize: 11, fontWeight: FontWeight.bold)),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length) {
                  return _buildTypingIndicator();
                }
                return _buildMessage(_messages[index]);
              },
            ),
          ),
          _buildInput(),
        ],
      ),
    );
  }

  Widget _buildMessage(Map<String, dynamic> msg) {
    final isUser = msg['role'] == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isUser ? const Color(0xFF5D3891) : const Color(0xFFF2F2F7),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(20),
            topRight: const Radius.circular(20),
            bottomLeft: Radius.circular(isUser ? 20 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 20),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (msg['hasImage'] == true) ...[
               Container(
                 height: 150, width: double.infinity,
                 margin: const EdgeInsets.only(bottom: 8),
                 decoration: BoxDecoration(
                   color: Colors.black12,
                   borderRadius: BorderRadius.circular(12),
                 ),
                 child: const Center(child: Icon(Icons.image_rounded, color: Colors.white70, size: 40)),
               ),
            ],
            Text(
              msg['text'] as String,
              style: TextStyle(
                color: isUser ? Colors.white : const Color(0xFF1F1F1F),
                height: 1.4,
                fontSize: 15,
                fontWeight: isUser ? FontWeight.w500 : FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFF2F2F7),
          borderRadius: BorderRadius.circular(20),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 12, height: 12,
              child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF5D3891)),
            ),
            SizedBox(width: 12),
            Text("AI is responding...", style: TextStyle(color: Color(0xFF8E8E93), fontSize: 13, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget _buildInput() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      decoration: const BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, -1))],
      ),
      child: Row(
        children: [
          IconButton(
            onPressed: _mockImageSelection,
            icon: Icon(Icons.camera_alt_rounded, color: _selectedImageBase64 != null ? const Color(0xFF00ADB5) : const Color(0xFF8E8E93)),
          ),
          IconButton(
            onPressed: _mockVoiceRecording,
            icon: Icon(Icons.mic_rounded, color: _selectedVoiceBase64 != null ? const Color(0xFFE71C23) : const Color(0xFF8E8E93)),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFFF2F2F7),
                borderRadius: BorderRadius.circular(24),
              ),
              child: TextField(
                controller: _controller,
                style: const TextStyle(color: Color(0xFF1F1F1F), fontSize: 15),
                decoration: const InputDecoration(
                  hintText: "Type or use voice/image...",
                  hintStyle: TextStyle(color: Color(0xFF8E8E93), fontSize: 14),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _sendMessage,
            child: Container(
              width: 44, height: 44,
              decoration: const BoxDecoration(
                color: Color(0xFF5D3891),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.arrow_upward_rounded, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }
}
