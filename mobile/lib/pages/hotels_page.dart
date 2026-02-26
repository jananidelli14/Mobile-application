import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';
import 'package:geolocator/geolocator.dart';

class HotelsPage extends StatefulWidget {
  const HotelsPage({super.key});

  @override
  State<HotelsPage> createState() => _HotelsPageState();
}

class _HotelsPageState extends State<HotelsPage> {
  final ApiService _apiService = ApiService();
  final LocationService _locationService = LocationService();
  List<dynamic> _hotels = [];
  bool _isLoading = true;
  String? _error;
  Position? _pos;

  @override
  void initState() {
    super.initState();
    _fetchHotels();
  }

  Future<void> _fetchHotels() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final pos = await _locationService.getCurrentLocation();
      setState(() => _pos = pos);
      if (pos != null) {
        final res = await _apiService.getNearbyHotels(pos.latitude, pos.longitude);
        if (mounted) {
          setState(() {
            _hotels = res['accommodations'] ?? res['hotels'] ?? [];
            _isLoading = false;
          });
        }
      } else {
        setState(() { _error = "Location permission needed."; _isLoading = false; });
      }
    } catch (e) {
      if (mounted) setState(() { _error = "Could not fetch hotels. Make sure backend is running."; _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverAppBar(
            expandedHeight: 140,
            pinned: true,
            elevation: 0,
            backgroundColor: Colors.white,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(color: Colors.white),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        const Text("Elite Stays", style: TextStyle(color: Color(0xFF1F1F1F), fontSize: 24, fontWeight: FontWeight.w900, letterSpacing: -0.5)),
                        const SizedBox(height: 4),
                        Text("Safety-vetted hotels for women travelers", style: TextStyle(color: const Color(0xFF8E8E93), fontSize: 13, fontWeight: FontWeight.w500)),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            actions: [
              Padding(
                padding: const EdgeInsets.only(right: 16),
                child: IconButton(
                  onPressed: _fetchHotels,
                  icon: const Icon(Icons.refresh_rounded, color: Color(0xFF5D3891)),
                ),
              ),
            ],
          ),

          if (_isLoading)
            const SliverFillRemaining(
              child: Center(child: CircularProgressIndicator(color: Color(0xFF5D3891))),
            )
          else if (_error != null)
            SliverFillRemaining(
              child: _buildError(),
            )
          else if (_hotels.isEmpty)
            SliverFillRemaining(
              child: _buildEmpty(),
            )
          else
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (ctx, index) => _buildHotelCard(_hotels[index]),
                  childCount: _hotels.length,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildHotelCard(dynamic hotel) {
    final rating = hotel['rating'] ?? hotel['safety_rating'] ?? 0.0;
    final ratingNum = rating is num ? rating.toDouble() : 0.0;
    final distance = hotel['distance_km'];
    final priceLevel = hotel['price_level'] ?? 2;
    final priceSigns = '\$' * (priceLevel is int ? priceLevel.clamp(1, 4) : 2);

    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFF2F2F7)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 20, offset: const Offset(0, 8))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: Text(hotel['name'] ?? 'Hotel', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: Color(0xFF1F1F1F), letterSpacing: -0.5))),
                    const SizedBox(width: 12),
                    if (ratingNum > 0)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(color: const Color(0xFFF9A826).withOpacity(0.08), borderRadius: BorderRadius.circular(10)),
                        child: Row(
                          children: [
                            const Icon(Icons.star_rounded, size: 16, color: Color(0xFFF9A826)),
                            const SizedBox(width: 4),
                            Text(ratingNum.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFFF9A826), fontSize: 13)),
                          ],
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(Icons.place_rounded, size: 14, color: Color(0xFF8E8E93)),
                    const SizedBox(width: 4),
                    Expanded(child: Text(hotel['address'] ?? hotel['vicinity'] ?? '', 
                        style: const TextStyle(color: Color(0xFF8E8E93), fontSize: 12, fontWeight: FontWeight.w500))),
                  ],
                ),
                if (distance != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Row(
                      children: [
                        const Icon(Icons.directions_walk_rounded, size: 14, color: Color(0xFF00ADB5)),
                        const SizedBox(width: 4),
                        Text("${distance} km away", style: const TextStyle(color: Color(0xFF00ADB5), fontSize: 12, fontWeight: FontWeight.w700)),
                      ],
                    ),
                  ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(color: const Color(0xFF00ADB5).withOpacity(0.08), borderRadius: BorderRadius.circular(12)),
                      child: const Row(
                        children: [
                          Icon(Icons.verified_user_rounded, size: 14, color: Color(0xFF00ADB5)),
                          SizedBox(width: 6),
                          Text("Safety Vetted", style: TextStyle(color: Color(0xFF00ADB5), fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 0.3)),
                        ],
                      ),
                    ),
                    const Spacer(),
                    Text(priceSigns, style: const TextStyle(color: Color(0xFF1F1F1F), fontWeight: FontWeight.w900, fontSize: 14)),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.hotel_outlined, size: 60, color: const Color(0xFFF2F2F7)),
            const SizedBox(height: 24),
            const Text('No Hotels Found', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20, color: Color(0xFF1F1F1F))),
            const SizedBox(height: 8),
            const Text('Add your Google Places API Key to the backend for real-time vetted results.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFF8E8E93), fontSize: 14)),
          ],
        ),
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded, size: 48, color: Color(0xFFE71C23)),
            const SizedBox(height: 16),
            Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF8E8E93), fontSize: 14)),
            const SizedBox(height: 24),
            TextButton.icon(onPressed: _fetchHotels, icon: const Icon(Icons.refresh_rounded), label: const Text('Try Again')),
          ],
        ),
      ),
    );
  }
}
