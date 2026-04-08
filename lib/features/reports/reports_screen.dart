import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../components/app_scaffold.dart';
import '../../components/app_widgets.dart';
import '../reports/reports_controller.dart';
import '../reports/widgets/report_widgets.dart';
import '../notifications/notifications_controller.dart';
import '../../app/routes.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  final int _selectedIndex = 1; // Default to Reports index in AppScaffold

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<ReportsController>();

    return AppScaffold(
      selectedIndex: _selectedIndex,
      onDestinationSelected: (idx) {
        if (idx == 0) Navigator.pushReplacementNamed(context, AppRoutes.dashboard);
        // Handle other indices if needed
      },
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            DashboardHeader(
              title: "Reports",
              onNotificationTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
              unreadCount: context.watch<NotificationsController>().unreadCount,
              onSettingsTap: () {},
            ),
            const Padding(
              padding: EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Scan history and threat analysis",
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            
            const ScanSummaryCard(),
            
            const ReportFilter(),
            
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: controller.reports.length,
              itemBuilder: (context, index) {
                final report = controller.reports[index];
                return ReportCard(
                  report: report,
                  onTap: () {
                    // Navigate to details (later)
                  },
                );
              },
            ),
            
            const SizedBox(height: 100),
          ],
        ),
      ),
    );
  }
}
