import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../components/app_scaffold.dart';
import '../../../components/app_widgets.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/responsive_helper.dart';
import '../notifications/notifications_controller.dart';
import 'app_scan_controller.dart';
import 'widgets/app_scan_widgets.dart';
import '../../../app/routes.dart';

class AppScanScreen extends StatefulWidget {
  const AppScanScreen({super.key});

  @override
  State<AppScanScreen> createState() => _AppScanScreenState();
}

class _AppScanScreenState extends State<AppScanScreen> {
  final int _selectedIndex = 0; // Keeping as Dashboard context since it's a sub-feature

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AppScanController>().reset();
    });
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<AppScanController>();

    return AppScaffold(
      selectedIndex: _selectedIndex,
      onDestinationSelected: (idx) {
        // Fallback for internal nav if AppScaffold handles differently
        Navigator.pop(context);
      },
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          children: [
            DashboardHeader(
              title: "App Scan",
              onNotificationTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
              unreadCount: context.watch<NotificationsController>().unreadCount,
              onSettingsTap: () {},
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Malware Check",
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                      color: AppColors.textDark,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    "Scan installed applications or analyze APK files for hidden threats.",
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 32),

                  if (controller.state == AppScanState.idle)
                    _buildSelectionView(controller),

                  if (controller.state == AppScanState.scanning)
                    ScanProgressWidget(
                      progress: controller.progress,
                      status: controller.statusMessage,
                    ),

                  if (controller.state == AppScanState.completed && controller.currentSession != null)
                    _buildResultPanel(context, controller),

                  if (controller.state == AppScanState.error)
                    _buildErrorView(controller),

                  const SizedBox(height: 100),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectionView(AppScanController controller) {
    return Column(
      children: [
        _SelectionCard(
          icon: Icons.apps,
          title: "Scan Installed Apps",
          subtitle: "Analyze all applications currently installed on your device.",
          color: AppColors.primaryBlue,
          onTap: () => controller.startDeviceScan(),
        ),
        const SizedBox(height: 16),
        _SelectionCard(
          icon: Icons.file_upload_outlined,
          title: "Upload APK File",
          subtitle: "Select an APK file to check for malicious modifications.",
          color: Colors.purple,
          onTap: () => controller.pickAndScanApk(),
        ),
      ],
    );
  }

  Widget _buildResultPanel(BuildContext context, AppScanController controller) {
    final session = controller.currentSession!;
    final safeApps = controller.scanResults.where((r) => r.isSafe).toList();
    final riskyApps = controller.scanResults.where((r) => !r.isSafe).toList();
    bool isAllSafe = riskyApps.isEmpty;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Score Header
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: isAllSafe ? Colors.green.withValues(alpha: 0.05) : Colors.red.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isAllSafe ? Colors.green.withValues(alpha: 0.2) : Colors.red.withValues(alpha: 0.2),
            ),
          ),
          child: Column(
            children: [
              Text(
                "Security Score: ${session.overallSecurityScore}%",
                style: TextStyle(
                  fontSize: Responsive.isSmallMobile(context) ? 24 : 28,
                  fontWeight: FontWeight.w900,
                  color: isAllSafe ? Colors.green[700] : Colors.redAccent,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                isAllSafe ? "Safe - Everything looks good." : "Risk Detected - Suspicious apps found.",
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: isAllSafe ? Colors.green[800] : Colors.red[800],
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _statItem("Total", session.totalAppsScanned.toString(), Colors.blue),
                  const SizedBox(width: 24),
                  _statItem("Safe", session.safeAppsCount.toString(), Colors.green),
                  const SizedBox(width: 24),
                  _statItem("Risks", session.riskyAppsCount.toString(), Colors.redAccent),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),

        if (riskyApps.isNotEmpty) ...[
          const Text(
            "Risk Apps",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.redAccent),
          ),
          const SizedBox(height: 12),
          ...riskyApps.map((app) => AppScanCard(
                result: app,
                isSelected: controller.selectedRiskyApps.contains(app.packageName),
                onToggleSelect: (val) => controller.toggleSelection(app.packageName),
                onUninstall: () => controller.uninstallApp(app.packageName),
                onIgnore: () => controller.ignoreApp(app.packageName),
              )),
          if (controller.selectedRiskyApps.isNotEmpty) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => controller.ignoreSelected(),
                    icon: const Icon(Icons.bookmark_added),
                    label: const Text("Keep Selected"),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.grey[700],
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => controller.uninstallSelected(),
                    icon: const Icon(Icons.delete_sweep),
                    label: const Text("Uninstall Selected"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.redAccent,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 24),
        ],

        if (safeApps.isNotEmpty) ...[
          const Text(
            "Safe Apps",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green),
          ),
          const SizedBox(height: 12),
          ...safeApps.map((app) => AppScanCard(
                result: app,
                onUninstall: () {},
                onIgnore: () {},
              )),
        ],

        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton(
            onPressed: () => controller.reset(),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: const Text("Scan Again"),
          ),
        ),
      ],
    );
  }

  Widget _statItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }

  Widget _buildErrorView(AppScanController controller) {
    return Center(
      child: Column(
        children: [
          const Icon(Icons.error_outline, color: Colors.redAccent, size: 64),
          const SizedBox(height: 16),
          Text(
            controller.statusMessage,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => controller.reset(),
            child: const Text("Try Again"),
          ),
        ],
      ),
    );
  }
}

class _SelectionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _SelectionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey.withValues(alpha: 0.1)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textDark,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 13,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }
}
