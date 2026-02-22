import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:io';

class PermissionsPage extends StatefulWidget {
  final VoidCallback onComplete;
  const PermissionsPage({super.key, required this.onComplete});

  @override
  State<PermissionsPage> createState() => _PermissionsPageState();
}

class _PermissionsPageState extends State<PermissionsPage> {
  bool _locationGranted = false;
  bool _notificationGranted = false;
  bool _smsGranted = false; // Simulated in Flutter web/Chrome demo
  bool _loading = false;

  Future<void> _requestLocation() async {
    final status = await Geolocator.requestPermission();
    setState(() {
      _locationGranted = status == LocationPermission.always || status == LocationPermission.whileInUse;
    });
  }

  void _requestDummyPermission(String type) {
    setState(() {
      if (type == 'sms') _smsGranted = true;
      if (type == 'notification') _notificationGranted = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.admin_panel_settings_rounded, size: 80, color: Color(0xFF5D3891)),
              const SizedBox(height: 32),
              const Text(
                "Trust & Safety",
                style: TextStyle(color: Color(0xFF1F1F1F), fontSize: 28, fontWeight: FontWeight.w900, letterSpacing: -1),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              const Text(
                "To provide full protection, SafeHer needs access to a few features on your device.",
                style: TextStyle(color: Color(0xFF8E8E93), fontSize: 14, fontWeight: FontWeight.w500),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              _permissionTile(
                icon: Icons.location_on_rounded,
                title: "Location Access",
                sub: "Required for live SOS tracking and finding nearby police.",
                granted: _locationGranted,
                onTap: _requestLocation,
              ),
              const SizedBox(height: 16),
              _permissionTile(
                icon: Icons.notifications_active_rounded,
                title: "Safety Notifications",
                sub: "Alerts about danger zones and emergency responses.",
                granted: _notificationGranted,
                onTap: () => _requestDummyPermission('notification'),
              ),
              const SizedBox(height: 16),
              _permissionTile(
                icon: Icons.sms_rounded,
                title: "SMS Dispatch",
                sub: "Automatic alerts to emergency contacts and police.",
                granted: _smsGranted,
                onTap: () => _requestDummyPermission('sms'),
              ),
              const Spacer(),
              ElevatedButton(
                onPressed: (_locationGranted) ? widget.onComplete : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF5D3891),
                  foregroundColor: Colors.white,
                  minimumSize: const Size.fromHeight(60),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                  elevation: 0,
                ),
                child: const Text("Continue to App", style: TextStyle(fontWeight: FontWeight.w900, fontSize: 16)),
              ),
              if (!_locationGranted)
                const Padding(
                  padding: EdgeInsets.only(top: 12),
                  child: Text(
                    "Location permission is mandatory for safety.",
                    style: TextStyle(color: Color(0xFFE71C23), fontSize: 11, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _permissionTile({required IconData icon, required String title, required String sub, required bool granted, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: granted ? null : onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: granted ? const Color(0xFF5D3891).withOpacity(0.05) : const Color(0xFFF2F2F7),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: granted ? const Color(0xFF5D3891).withOpacity(0.1) : Colors.transparent),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: granted ? const Color(0xFF5D3891) : Colors.white,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: granted ? Colors.white : const Color(0xFF5D3891), size: 20),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15, color: Color(0xFF1F1F1F))),
                  const SizedBox(height: 2),
                  Text(sub, style: const TextStyle(color: Color(0xFF8E8E93), fontSize: 11, fontWeight: FontWeight.w500)),
                ],
              ),
            ),
            Icon(
              granted ? Icons.check_circle_rounded : Icons.add_circle_outline_rounded,
              color: granted ? const Color(0xFF00ADB5) : const Color(0xFF8E8E93),
            ),
          ],
        ),
      ),
    );
  }
}
