import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';
import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';

class ResourcesPage extends StatefulWidget {
  const ResourcesPage({super.key});

  @override
  State<ResourcesPage> createState() => _ResourcesPageState();
}

class _ResourcesPageState extends State<ResourcesPage> {
  final ApiService _apiService = ApiService();
  final LocationService _locationService = LocationService();
  
  List<dynamic> _resources = [];
  bool _isLoading = true;
  Position? _currentPos;
  String _selectedCategory = 'police'; // 'police' or 'hospital'

  @override
  void initState() {
    super.initState();
    _loadResources();
  }

  Future<void> _loadResources() async {
    setState(() => _isLoading = true);
    try {
      final pos = await _locationService.getCurrentLocation();
      if (pos == null) throw Exception("Could not get location");
      _currentPos = pos;
      
      final response = _selectedCategory == 'police' 
          ? await _apiService.getNearbyPolice(pos.latitude, pos.longitude)
          : await _apiService.getNearbyHospitals(pos.latitude, pos.longitude);
          
      if (mounted) {
        setState(() {
          _resources = response['stations'] ?? response['hospitals'] ?? [];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          "Emergency Resources",
          style: TextStyle(color: Color(0xFF1F1F1F), fontWeight: FontWeight.w900, fontSize: 20),
        ),
        actions: [
          IconButton(
            onPressed: _loadResources,
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF5D3891)),
          )
        ],
      ),
      body: Column(
        children: [
          _buildCategoryToggle(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF5D3891)))
                : _resources.isEmpty
                    ? _buildEmptyState()
                    : ListView.builder(
                        padding: const EdgeInsets.all(24),
                        itemCount: _resources.length,
                        itemBuilder: (ctx, i) => _buildResourceCard(_resources[i]),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryToggle() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 0),
      child: Row(
        children: [
          _toggleItem("Police", 'police', Icons.security_rounded),
          const SizedBox(width: 12),
          _toggleItem("Hospitals", 'hospital', Icons.medical_services_rounded),
        ],
      ),
    );
  }

  Widget _toggleItem(String label, String val, IconData icon) {
    final isSel = _selectedCategory == val;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            _selectedCategory = val;
            _loadResources();
          });
        },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSel ? const Color(0xFF5D3891) : const Color(0xFFF2F2F7),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: isSel ? Colors.white : const Color(0xFF5D3891), size: 16),
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  color: isSel ? Colors.white : const Color(0xFF1F1F1F),
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.security_rounded, size: 64, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            "No police stations found nearby",
            style: TextStyle(color: Colors.grey[600], fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildResourceCard(dynamic station) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFF2F2F7),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.black.withOpacity(0.03)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF5D3891).withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.local_police_rounded, color: Color(0xFF5D3891), size: 20),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      station['name'] ?? 'Police Station',
                      style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: Color(0xFF1F1F1F)),
                    ),
                    Text(
                      "${station['distance_km']} km away",
                      style: const TextStyle(color: Color(0xFF00ADB5), fontWeight: FontWeight.w800, fontSize: 13),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(height: 1),
          const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.location_on_rounded, size: 14, color: Color(0xFF8E8E93)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    station['address'] ?? 'Tamil Nadu, India',
                    style: const TextStyle(color: Color(0xFF8E8E93), fontSize: 12),
                  ),
                ),
              ],
            ),
            if (station['phone'] != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.phone_rounded, size: 14, color: Color(0xFF00ADB5)),
                  const SizedBox(width: 8),
                  Text(
                    station['phone'],
                    style: const TextStyle(color: Color(0xFF00ADB5), fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _actionButton(
                  icon: Icons.phone_rounded,
                  label: "Call Help",
                  color: const Color(0xFF5D3891),
                  onTap: () async {
                    final phone = station['phone'] ?? '100';
                    final uri = Uri.parse('tel:$phone');
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri);
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _actionButton(
                  icon: Icons.directions_rounded,
                  label: "Navigate",
                  color: const Color(0xFF00ADB5),
                  onTap: () async {
                    final lat = station['lat'];
                    final lng = station['lng'];
                    final name = Uri.encodeComponent(station['name'] ?? 'Resource');
                    final uri = Uri.parse('https://www.google.com/maps/search/?api=1&query=$lat,$lng');
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri);
                    }
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _actionButton({required IconData icon, required String label, required Color color, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 14),
            const SizedBox(width: 6),
            Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}
