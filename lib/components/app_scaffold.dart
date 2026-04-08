import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../core/utils/responsive_helper.dart';
import '../app/routes.dart';

class AppScaffold extends StatelessWidget {
  final Widget body;
  final int selectedIndex;
  final Function(int) onDestinationSelected;
  final String title;

  const AppScaffold({
    super.key,
    required this.body,
    required this.selectedIndex,
    required this.onDestinationSelected,
    this.title = "AppGuardAi",
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Desktop is 1024+ or if user says 800+
        bool isDesktop = constraints.maxWidth >= 800;
        bool isTiny = constraints.maxWidth <= 320;

        return Scaffold(
          backgroundColor: const Color(0xFFF9FAFC),
          body: Row(
            children: [
              if (isDesktop) _buildSidebar(context),
              Expanded(
                child: SafeArea(
                  child: body,
                ),
              ),
            ],
          ),
          bottomNavigationBar: isDesktop ? null : _buildBottomNav(context, isTiny, selectedIndex),
        );
      },
    );
  }

  void _handleNavigation(BuildContext context, int index) {
    if (index == selectedIndex) return;
    
    switch (index) {
      case 0:
        Navigator.pushReplacementNamed(context, AppRoutes.dashboard);
        break;
      case 1:
        Navigator.pushReplacementNamed(context, AppRoutes.reports);
        break;
      case 2:
        Navigator.pushReplacementNamed(context, AppRoutes.notifications);
        break;
      case 3:
        Navigator.pushReplacementNamed(context, AppRoutes.settings);
        break;
      // Other cases can be added as screens are ready
    }
  }

  Widget _buildSidebar(BuildContext context) {
    return Container(
      width: math.min(Responsive.width(context) * 0.25, 260),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(right: BorderSide(color: Colors.grey.withValues(alpha: 0.1))),
      ),
      child: Column(
        children: [
          const SizedBox(height: 48),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Image.asset('assets/logos/logo.png', height: 40, width: 40),
                const SizedBox(width: 8),
                Flexible(
                  child: RichText(
                    text: const TextSpan(
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        fontFamily: 'Inter',
                      ),
                      children: [
                        TextSpan(
                          text: "AppGuard",
                          style: TextStyle(color: AppColors.textDark),
                        ),
                        TextSpan(
                          text: "Ai",
                          style: TextStyle(color: AppColors.primaryBlue),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 40),
          _sidebarItem(context, 0, Icons.home_filled, "Home"),
          _sidebarItem(context, 1, Icons.assessment_outlined, "Reports"),
          _sidebarItem(context, 2, Icons.notifications_none, "Notification"),
          _sidebarItem(context, 3, Icons.person_outline, "Settings"),
        ],
      ),
    );
  }

  Widget _sidebarItem(BuildContext context, int index, IconData icon, String label) {
    bool isSelected = selectedIndex == index;
    return ListTile(
      onTap: () => _handleNavigation(context, index),
      contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 4),
      leading: Icon(icon, color: isSelected ? AppColors.primaryBlue : Colors.grey[400]),
      title: Text(
        label,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(
          color: isSelected ? AppColors.primaryBlue : Colors.grey[600],
          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
        ),
      ),
      selected: isSelected,
      selectedTileColor: AppColors.primaryBlue.withValues(alpha: 0.05),
    );
  }

  Widget _buildBottomNav(BuildContext context, bool isTiny, int selectedIndex) {
    return Container(
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10, offset: const Offset(0, -2))
        ],
      ),
      child: BottomNavigationBar(
        currentIndex: selectedIndex,
        onTap: (index) => _handleNavigation(context, index),
        selectedLabelStyle: TextStyle(fontSize: isTiny ? 10 : 12),
        unselectedLabelStyle: TextStyle(fontSize: isTiny ? 10 : 12),
        selectedItemColor: AppColors.primaryBlue,
        unselectedItemColor: Colors.grey[400],
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        iconSize: isTiny ? 20 : 24,
        showSelectedLabels: true,
        showUnselectedLabels: true,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_filled), label: "Home"),
          BottomNavigationBarItem(icon: Icon(Icons.assessment_outlined), label: "Reports"),
          BottomNavigationBarItem(icon: Icon(Icons.notifications_none), label: "Notification"),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), label: "Settings"),
        ],
      ),
    );
  }
}

