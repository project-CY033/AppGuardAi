import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../components/app_scaffold.dart';
import '../../../components/app_widgets.dart';
import '../notifications/notifications_controller.dart';
import 'settings_controller.dart';
import 'widgets/settings_widgets.dart';
import '../../../app/routes.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<SettingsController>();

    return AppScaffold(
      selectedIndex: 3, // Assuming 3 is settings index in AppScaffold (it is index 3 in sidebar)
      onDestinationSelected: (idx) {}, // AppScaffold handles navigation
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          children: [
            DashboardHeader(
              title: "Settings",
              onNotificationTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
              unreadCount: context.watch<NotificationsController>().unreadCount,
              onSettingsTap: null, // Don't show settings icon on settings page
            ),
            
            // Basic Settings
            const SettingsSectionHeader(title: "BASIC SETTINGS"),
            SettingsSwitchTile(
              title: "Enable Notifications",
              subtitle: "Receive alerts for security events and scans.",
              icon: Icons.notifications_active_outlined,
              value: controller.notificationsEnabled,
              onChanged: (v) => controller.toggleNotifications(v),
            ),
            SettingsSwitchTile(
              title: "Dark Mode",
              subtitle: "Switch between light and dark visual themes.",
              icon: Icons.dark_mode_outlined,
              value: controller.darkMode,
              onChanged: (v) => controller.toggleDarkMode(v),
            ),
            SettingsSwitchTile(
              title: "Auto-Scan on Install",
              subtitle: "Automatically check new apps for malware.",
              icon: Icons.system_security_update_good_outlined,
              value: controller.autoScanOnInstall,
              onChanged: (v) => controller.toggleAutoScan(v),
            ),
            SettingsDropdownTile(
              title: "Scan Frequency",
              subtitle: "How often background scans should run.",
              icon: Icons.schedule,
              value: controller.scanFrequency,
              items: const ['Manual', 'Daily', 'Weekly'],
              onChanged: (v) {
                if (v != null) controller.setScanFrequency(v);
              },
            ),

            // Advanced Security
            const SettingsSectionHeader(title: "ADVANCED SECURITY"),
            SettingsSwitchTile(
              title: "Real-Time Protection",
              subtitle: "Actively monitor memory and processes.",
              icon: Icons.security,
              value: controller.realTimeProtection,
              onChanged: (v) => controller.toggleRealTimeProtection(v),
            ),
            SettingsSwitchTile(
              title: "Background Scanning",
              subtitle: "Allow scans while app is minimized.",
              icon: Icons.sync,
              value: controller.backgroundScanning,
              onChanged: (v) => controller.toggleBackgroundScanning(v),
            ),
            SettingsSwitchTile(
              title: "Deep Scan Mode",
              subtitle: "Thoroughly inspect all files and archives.",
              icon: Icons.search_outlined,
              value: controller.deepScanMode,
              onChanged: (v) => controller.toggleDeepScanMode(v),
            ),
            SettingsSwitchTile(
              title: "Network Monitoring",
              subtitle: "Track suspicious outgoing connections.",
              icon: Icons.network_check_outlined,
              value: controller.networkMonitoring,
              onChanged: (v) => controller.toggleNetworkMonitoring(v),
            ),
            SettingsDropdownTile(
              title: "Threat Sensitivity",
              subtitle: "Adjust detection aggressiveness.",
              icon: Icons.policy_outlined,
              value: controller.threatSensitivity,
              items: const ['Low', 'Medium', 'High'],
              onChanged: (v) {
                if (v != null) controller.setThreatSensitivity(v);
              },
            ),

            // Privacy & Data
            const SettingsSectionHeader(title: "PRIVACY & DATA"),
            SettingsSwitchTile(
              title: "Share Anonymized Data",
              subtitle: "Help us improve threat detection.",
              icon: Icons.data_usage,
              value: controller.shareAnonymizedData,
              onChanged: (v) => controller.toggleAnonymizedData(v),
            ),
            SettingsActionTile(
              title: "Clear Scan History",
              subtitle: "Remove all past reports and scan logs.",
              icon: Icons.delete_sweep_outlined,
              onTap: () async {
                await controller.clearScanHistory();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Scan history cleared')),
                  );
                }
              },
            ),
            SettingsActionTile(
              title: "Reset All Settings",
              subtitle: "Restore application defaults securely.",
              icon: Icons.restore,
              isDestructive: true,
              onTap: () async {
                await controller.resetAllSettings();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Settings reset to defaults')),
                  );
                }
              },
            ),

            // About
            const SettingsSectionHeader(title: "ABOUT APPGUARDAI"),
            const ListTile(
              contentPadding: EdgeInsets.symmetric(horizontal: 24, vertical: 4),
              leading: Icon(Icons.info_outline, color: Colors.grey),
              title: Text("Version", style: TextStyle(fontWeight: FontWeight.w600)),
              subtitle: Text("1.0.0 (Build 30)"),
            ),
            const ListTile(
              contentPadding: EdgeInsets.symmetric(horizontal: 24, vertical: 4),
              leading: Icon(Icons.code, color: Colors.grey),
              title: Text("Developer", style: TextStyle(fontWeight: FontWeight.w600)),
              subtitle: Text("AppGuard Security Team"),
            ),
            const ListTile(
              contentPadding: EdgeInsets.symmetric(horizontal: 24, vertical: 4),
              leading: Icon(Icons.privacy_tip_outlined, color: Colors.grey),
              title: Text("Privacy Policy", style: TextStyle(fontWeight: FontWeight.w600)),
              subtitle: Text("View our terms and privacy guidelines"),
              trailing: Icon(Icons.open_in_new, color: Colors.grey, size: 18),
            ),

            const SizedBox(height: 64),
          ],
        ),
      ),
    );
  }
}
