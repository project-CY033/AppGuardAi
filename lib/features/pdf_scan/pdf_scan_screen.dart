import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../components/app_scaffold.dart';
import '../../components/app_widgets.dart';
import '../../app/routes.dart';
import '../../core/theme/app_theme.dart';
import 'pdf_scan_controller.dart';
import '../notifications/notifications_controller.dart';
import 'widgets/pdf_widgets.dart';

class PdfScanScreen extends StatefulWidget {
  const PdfScanScreen({super.key});

  @override
  State<PdfScanScreen> createState() => _PdfScanScreenState();
}

class _PdfScanScreenState extends State<PdfScanScreen> {
  final int _selectedIndex = 0; // Keeping as dashboard context or handle properly

  @override
  void initState() {
    super.initState();
    // Ensure idle state when entering
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PdfScanController>().reset();
    });
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<PdfScanController>();

    return AppScaffold(
      selectedIndex: _selectedIndex,
      onDestinationSelected: (idx) {
        // Since this is a sub-page, we might want to pop or handle global nav
        Navigator.pop(context);
      },
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          children: [
            DashboardHeader(
              title: "PDF Security Scan",
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
                    "Advanced document analysis engine to detect malicious scripts and hidden threats.",
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 32),
                  
                  // Conditional UI based on state
                  if (controller.state == PdfScanState.idle || controller.state == PdfScanState.uploading)
                    _buildUploadView(controller),
                  
                  if (controller.state == PdfScanState.scanning)
                    PdfScanningView(
                      progress: controller.progress,
                      status: controller.statusMessage,
                    ),
                  
                  if (controller.state == PdfScanState.completed && controller.lastReport != null)
                    PdfResultPanel(
                      report: controller.lastReport!,
                      onReset: () => controller.reset(),
                    ),
                  
                  if (controller.state == PdfScanState.error)
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

  Widget _buildUploadView(PdfScanController controller) {
    return Column(
      children: [
        PdfUploadCard(
          fileName: controller.selectedFile?.name,
          fileSize: controller.selectedFile != null ? "${(controller.selectedFile!.size / 1024).toStringAsFixed(1)} KB" : null,
          onTap: () => controller.pickFile(),
        ),
        const SizedBox(height: 32),
        if (controller.selectedFile != null)
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => controller.startScan(),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primaryBlue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 0,
              ),
              child: const Text(
                "Scan PDF Now",
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildErrorView(PdfScanController controller) {
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
