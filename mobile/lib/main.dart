import 'package:flutter/material.dart';
import 'pages/dashboard_page.dart';
import 'pages/chat_page.dart';
import 'pages/sos_page.dart';
import 'pages/resources_page.dart';
import 'pages/hotels_page.dart';
import 'pages/map_page.dart';
import 'pages/community_page.dart';
import 'pages/login_page.dart';
import 'pages/permissions_page.dart';
import 'services/auth_service.dart';
import 'package:geolocator/geolocator.dart';

void main() {
  runApp(const SafeHerApp());
}

class SafeHerApp extends StatelessWidget {
  const SafeHerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Safe Her Travel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF5D3891), // Professional Purple
          brightness: Brightness.light,
        ).copyWith(
          primary: const Color(0xFF5D3891),
          secondary: const Color(0xFFE71C23), // SOS Red
          tertiary: const Color(0xFF00ADB5), // Professional Teal
          surface: Colors.white,
        ),
        scaffoldBackgroundColor: Colors.white,
        useMaterial3: true,
        fontFamily: 'Roboto',
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          elevation: 0,
          iconTheme: IconThemeData(color: Color(0xFF2D31FA)),
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          color: Colors.white,
          shadowColor: Colors.black.withOpacity(0.1),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
      home: const AuthGate(),
    );
  }
}

/// Decides whether to show Login or Main shell based on session
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _checking = true;
  bool _loggedIn = false;
  bool _permissionsNeeded = true;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final loggedIn = await AuthService.isLoggedIn();
    bool permissionsNeeded = true;
    
    if (loggedIn) {
      final status = await Geolocator.checkPermission();
      permissionsNeeded = status == LocationPermission.denied || status == LocationPermission.deniedForever;
    }

    if (mounted) {
      setState(() {
        _loggedIn = loggedIn;
        _permissionsNeeded = permissionsNeeded;
        _checking = false;
      });
    }
  }

  void _onLoginSuccess() {
    setState(() => _loggedIn = true);
  }

  void _onLogout() {
    AuthService.logout().then((_) {
      if (mounted) setState(() => _loggedIn = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(
        backgroundColor: Colors.white,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.shield_rounded, color: Color(0xFFE71C23), size: 64),
              SizedBox(height: 24),
              CircularProgressIndicator(color: Color(0xFF5D3891)),
            ],
          ),
        ),
      );
    }

    if (!_loggedIn) {
      return LoginPage(onLoginSuccess: () {
        setState(() {
          _loggedIn = true;
          _permissionsNeeded = true;
        });
      });
    }

    if (_permissionsNeeded) {
      return PermissionsPage(onComplete: () {
        setState(() => _permissionsNeeded = false);
      });
    }

    return MainShell(onLogout: _onLogout);
  }
}

class MainShell extends StatefulWidget {
  final VoidCallback onLogout;
  const MainShell({super.key, required this.onLogout});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _selectedIndex = 0;

  late final List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    _pages = [
      DashboardPage(onNavigate: (index) => setState(() => _selectedIndex = index)),
      const ChatPage(),
      const SOSPage(),
      const MapPage(),
      const ResourcesPage(),
      const HotelsPage(),
      const CommunityPage(),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _pages,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.10), blurRadius: 20, offset: const Offset(0, -4))],
        ),
        child: SafeArea(
          top: false,
          child: SizedBox(
            height: 62,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _navItem(0, Icons.home_outlined, Icons.home_rounded, 'Home'),
                _navItem(1, Icons.chat_bubble_outline_rounded, Icons.chat_bubble_rounded, 'Chat'),
                _navItem(2, Icons.sos_outlined, Icons.sos_rounded, 'SOS', highlight: true),
                _navItem(3, Icons.map_outlined, Icons.map_rounded, 'Map'),
                _navItem(4, Icons.shield_outlined, Icons.shield_rounded, 'Safety'),
                _navItem(5, Icons.hotel_outlined, Icons.hotel_rounded, 'Hotels'),
                _navItem(6, Icons.people_outline_rounded, Icons.people_rounded, 'Community'),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _navItem(int index, IconData icon, IconData activeIcon, String label, {bool highlight = false}) {
    final isActive = _selectedIndex == index;
    final activeColor = highlight ? const Color(0xFFE71C23) : const Color(0xFF5D3891);
    return GestureDetector(
      onTap: () => setState(() => _selectedIndex = index),
      behavior: HitTestBehavior.opaque,
      child: SizedBox(
        width: 48,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: isActive ? activeColor.withOpacity(0.12) : Colors.transparent,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                isActive ? activeIcon : icon,
                color: isActive ? activeColor : Colors.grey,
                size: 22,
              ),
            ),
            Text(label,
              style: TextStyle(
                fontSize: 9,
                fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                color: isActive ? activeColor : Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
