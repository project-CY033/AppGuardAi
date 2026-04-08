import 'package:flutter/material.dart';
import 'package:android_intent_plus/android_intent.dart';
import '../../core/theme/app_theme.dart';
import 'manage_apps_controller.dart';

class AppInfoScreen extends StatelessWidget {
  final MockAppDetails appDetails;

  const AppInfoScreen({super.key, required this.appDetails});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textDark),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert, color: AppColors.textDark),
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildAppHeader(appDetails),
            const Divider(height: 1),
            _buildInfoSection(context, "Storage", appDetails.storageSize),
            _buildInfoSection(context, "Data usage", "Data usage 0 B"),
            _buildInfoSection(context, "Battery", "Battery usage 0.0%"),
            const SizedBox(height: 20),
            _buildSectionHeader("Permissions"),
            _buildSwitchItem("Pause app activity if unused", "Remove permissions, delete temporary files, and stop notifications"),
            _buildArrowItem("App permissions", "Manage permissions related to location, storage, phone, messages, and contacts."),
            _buildArrowItem("Other permissions", null),
            _buildArrowItem("Notifications", "No"),
            const SizedBox(height: 20),
            _buildSectionHeader("Advanced settings"),
            _buildArrowItem("Clear defaults", "No defaults set."),
            const SizedBox(height: 100), // Space for bottom actions
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomActions(context),
    );
  }

  Widget _buildAppHeader(MockAppDetails details) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Row(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(15),
            ),
            child: details.app.icon != null 
                ? Image.memory(details.app.icon!, fit: BoxFit.contain)
                : const Icon(Icons.android, size: 40, color: Colors.grey),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  details.app.name,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textDark,
                  ),
                ),
                Text(
                  "Version: ${details.app.versionName}",
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoSection(BuildContext context, String title, String value) {
    return InkWell(
      onTap: () => _openSettings(),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.textDark,
              ),
            ),
            Row(
              children: [
                Text(
                  value,
                  style: const TextStyle(color: Colors.grey, fontSize: 14),
                ),
                const SizedBox(width: 8),
                const Icon(Icons.chevron_right, color: Colors.grey, size: 20),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.indigo[900]?.withValues(alpha: 0.5),
        ),
      ),
    );
  }

  Widget _buildSwitchItem(String title, String subtitle) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          Switch(
            value: true,
            onChanged: (val) {},
            activeThumbColor: Colors.blue,
          ),
        ],
      ),
    );
  }

  Widget _buildArrowItem(String title, String? value) {
    return InkWell(
      onTap: () => _openSettings(),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textDark,
                    ),
                  ),
                  if (value != null && value.length > 30) ...[
                    const SizedBox(height: 4),
                    Text(
                      value,
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ],
              ),
            ),
            if (value != null && value.length <= 30) 
              Text(
                value,
                style: const TextStyle(color: Colors.grey, fontSize: 14),
              ),
            const SizedBox(width: 8),
            const Icon(Icons.chevron_right, color: Colors.grey, size: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomActions(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Colors.grey.withValues(alpha: 0.2))),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _bottomActionItem(Icons.close, "Force stop", () => _openSettings()),
          _bottomActionItem(Icons.delete_outline, "Uninstall", () => _uninstallApp()),
          _bottomActionItem(Icons.cleaning_services_outlined, "Clear data", () => _openSettings()),
        ],
      ),
    );
  }

  Widget _bottomActionItem(IconData icon, String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: AppColors.textDark, size: 24),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(fontSize: 12, color: AppColors.textDark),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _openSettings() async {
    final intent = AndroidIntent(
      action: 'android.settings.APPLICATION_DETAILS_SETTINGS',
      data: 'package:${appDetails.app.packageName}',
    );
    await intent.launch();
  }

  Future<void> _uninstallApp() async {
    final intent = AndroidIntent(
      action: 'android.intent.action.DELETE',
      data: 'package:${appDetails.app.packageName}',
    );
    await intent.launch();
  }
}
