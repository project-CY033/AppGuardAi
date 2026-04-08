import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../components/app_scaffold.dart';
import '../../components/app_widgets.dart';
import '../../core/theme/app_theme.dart';
import '../../core/utils/responsive_helper.dart';
import '../../app/routes.dart';
import 'dashboard_controller.dart';
import '../notifications/notifications_controller.dart';
import 'dart:math' as math;
import 'widgets/results_bottom_sheet.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with SingleTickerProviderStateMixin {
  int _selectedIndex = 0;
  late AnimationController _scannerController;

  @override
  void initState() {
    super.initState();
    _scannerController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    );
  }

  @override
  void dispose() {
    _scannerController.dispose();
    super.dispose();
  }

  void _triggerScan() {
    final controller = context.read<DashboardController>();
    controller.performScan(context, onComplete: () {
      if (mounted) {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Colors.transparent,
          builder: (ctx) => FractionallySizedBox(
            heightFactor: 0.85,
            child: ResultsBottomSheet(controller: controller),
          ),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<DashboardController>();
    final notificationController = context.watch<NotificationsController>();
    
    // Sync animation with state
    if (controller.state == ScanState.scanning) {
      if (!_scannerController.isAnimating) _scannerController.repeat();
    } else {
      _scannerController.stop();
    }

    return AppScaffold(
      selectedIndex: _selectedIndex,
      onDestinationSelected: (idx) => setState(() => _selectedIndex = idx),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          children: [
            DashboardHeader(
              title: "AppGuardAi",
              onNotificationTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
              unreadCount: notificationController.unreadCount,
              onSettingsTap: () => Navigator.pushNamed(context, AppRoutes.settings),
            ),
            
            _buildScannerSection(context, controller),
            
            const SizedBox(height: 32),
            
            _buildOptimizationSection(context),

            const SizedBox(height: 32),
            
            _buildSecurityToolsSection(context),

            const SizedBox(height: 32),
            
            _buildAppManagementSection(context),
            
            const SizedBox(height: 100), // Space for bottom nav/scrolling
          ],
        ),
      ),
    );
  }

  Widget _buildScannerSection(BuildContext context, DashboardController controller) {
    double screenWidth = Responsive.width(context);
    double scannerSize = Responsive.isSmallMobile(context) ? 220 : math.min(screenWidth * 0.7, 300);

    return Column(
      children: [
        SizedBox(
          height: scannerSize,
          width: scannerSize,
          child: Stack(
            alignment: Alignment.center,
            children: [
              AnimatedScanner(
                controller: _scannerController,
                state: controller.state,
                progress: controller.progress,
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    controller.state == ScanState.idle 
                        ? "Scan Now" 
                        : controller.state == ScanState.scanning
                            ? "${controller.progress.toInt()}%"
                            : "${controller.score.toInt()}%",
                    style: TextStyle(
                      fontSize: Responsive.isSmallMobile(context) ? 32 : 44,
                      fontWeight: FontWeight.w900,
                      color: controller.state == ScanState.risk ? Colors.redAccent : AppColors.primaryBlue,
                    ),
                  ),
                  if (controller.state != ScanState.idle)
                    FittedBox(
                      child: Text(
                        controller.state == ScanState.scanning ? "Analyzing System..." : (controller.score >= 80 ? "Secure" : "Critical Risk"),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: controller.state == ScanState.risk ? Colors.redAccent : AppColors.textDark.withValues(alpha: 0.6),
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            child: Text(
              controller.status,
              key: ValueKey<String>(controller.status),
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: Responsive.isSmallMobile(context) ? 14 : 16,
                fontWeight: FontWeight.w600,
                color: controller.state == ScanState.risk ? Colors.redAccent : AppColors.textDark,
              ),
            ),
          ),
        ),
        const SizedBox(height: 24),
        if (controller.state == ScanState.idle || controller.state == ScanState.safe || controller.state == ScanState.risk)
          ElevatedButton(
            onPressed: _triggerScan,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primaryBlue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              elevation: 4,
              shadowColor: AppColors.primaryBlue.withValues(alpha: 0.4),
            ),
            child: Text(
              controller.state == ScanState.idle ? "START FULL SCAN" : "RESCAN DEVICE",
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, letterSpacing: 1),
            ),
          ),
      ],
    );
  }

  Widget _buildOptimizationSection(BuildContext context) {
    double spacing = Responsive.isSmallMobile(context) ? 12 : 16;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 24),
          child: Text(
            "Device Optimization",
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textDark,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: LayoutBuilder(
            builder: (context, constraints) {
              double cardWidth = (constraints.maxWidth - spacing) / 2;
              double cardHeight = Responsive.isSmallMobile(context) ? 120 : 130;
              double aspectRatio = cardWidth / cardHeight;

              return GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                mainAxisSpacing: spacing,
                crossAxisSpacing: spacing,
                childAspectRatio: aspectRatio,
                children: [
                  _optimizationCard(
                    context,
                    icon: Icons.rocket_launch_rounded,
                    title: "Boost Speed",
                    subtitle: "Free up RAM",
                    onTap: () => Navigator.pushNamed(context, AppRoutes.boostSpeed),
                    gradient: LinearGradient(
                      colors: [Colors.greenAccent.shade400, Colors.greenAccent.shade700],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  _optimizationCard(
                    context,
                    icon: Icons.cleaning_services_rounded,
                    title: "Deep Clean",
                    subtitle: "Reclaim Storage",
                    onTap: () => Navigator.pushNamed(context, AppRoutes.deepClean),
                    gradient: LinearGradient(
                      colors: [Colors.orangeAccent.shade200, Colors.orangeAccent.shade400],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _optimizationCard(BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    required Gradient gradient,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: gradient,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: (gradient as LinearGradient).colors.first.withValues(alpha: 0.3),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 32),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 11,
                color: Colors.white70,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSecurityToolsSection(BuildContext context) {
    double spacing = Responsive.isSmallMobile(context) ? 12 : 16;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 24),
          child: Text(
            "Security Tools",
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textDark,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: LayoutBuilder(
            builder: (context, constraints) {
              double cardWidth = (constraints.maxWidth - spacing) / 2;
              double cardHeight = Responsive.isSmallMobile(context) ? 100 : 110;
              double aspectRatio = cardWidth / cardHeight;

              return GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                mainAxisSpacing: spacing,
                crossAxisSpacing: spacing,
                childAspectRatio: aspectRatio,
                children: [
                  _securityToolItem(context, Icons.apps_outlined, "Apps Scan", Colors.blueAccent,
                    onTap: () => Navigator.pushNamed(context, AppRoutes.appScan)),
                  _securityToolItem(context, Icons.picture_as_pdf_outlined, "PDF Scan", Colors.redAccent,
                    onTap: () => Navigator.pushNamed(context, AppRoutes.pdfScan)),
                  _securityToolItem(context, Icons.description_outlined, "Reports", Colors.purpleAccent,
                    onTap: () => Navigator.pushNamed(context, AppRoutes.reports)),
                  _securityToolItem(context, Icons.lock_outline, "App Lock", Colors.green,
                    onTap: () {}), // Placeholder for App Lock
                  _securityToolItem(context, Icons.wifi, "Wi-Fi Security", Colors.indigo,
                    onTap: () {}), // Placeholder for Wi-Fi Security
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _securityToolItem(BuildContext context, IconData icon, String label, Color color, {VoidCallback? onTap}) {
    bool isTiny = Responsive.isSmallMobile(context);
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10, offset: const Offset(0, 4))
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: isTiny ? 24 : 28),
            const SizedBox(height: 8),
            Flexible(
              child: Text(
                label,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.visible,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textDark,
                  height: 1.1,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppManagementSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 24),
          child: Text(
            "App Management",
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textDark,
            ),
          ),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: GestureDetector(
            onTap: () => Navigator.pushNamed(context, AppRoutes.manageApps),
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.teal.shade400, Colors.teal.shade700],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.teal.withValues(alpha: 0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.2),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.settings_applications_rounded, color: Colors.white, size: 32),
                  ),
                  const SizedBox(width: 20),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "Manage Apps",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          "Control all your applications",
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios, color: Colors.white, size: 18),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class AnimatedScanner extends StatelessWidget {
  final Animation<double> controller;
  final ScanState state;
  final double progress;

  const AnimatedScanner({
    super.key,
    required this.controller,
    required this.state,
    required this.progress,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        return CustomPaint(
          painter: ScannerPainter(
            animation: controller.value,
            state: state,
            progress: progress,
          ),
          child: Container(),
        );
      },
    );
  }
}

class ScannerPainter extends CustomPainter {
  final double animation;
  final ScanState state;
  final double progress;

  ScannerPainter({
    required this.animation,
    required this.state,
    required this.progress,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;

    Color primaryThemeColor = state == ScanState.risk ? Colors.redAccent : AppColors.primaryBlue;

    // Soft Shadow outer glow
    final shadowPaint = Paint()
      ..color = primaryThemeColor.withValues(alpha: 0.08 + (0.05 * math.sin(animation * math.pi * 2)))
      ..style = PaintingStyle.fill
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 20);
    canvas.drawCircle(center, radius + 10, shadowPaint);

    // Inner Background circle (glassmorphism feel)
    final bgPaint = Paint()
      ..color = primaryThemeColor.withValues(alpha: 0.03)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, radius, bgPaint);

    // Track Circle
    final trackCirclePaint = Paint()
      ..color = primaryThemeColor.withValues(alpha: 0.08)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10;
    canvas.drawCircle(center, radius, trackCirclePaint);

    // Dash pattern or Radar line logic
    if (state == ScanState.scanning) {
      final sweepAngle = (progress / 100) * 2 * math.pi;
      
      // Radar gradient scan arm
      final scanArmPaint = Paint()
        ..shader = SweepGradient(
          colors: [
            primaryThemeColor.withValues(alpha: 0.0),
            primaryThemeColor.withValues(alpha: 0.8),
          ],
          stops: const [0.6, 1.0],
        ).createShader(Rect.fromCircle(center: center, radius: radius))
        ..style = PaintingStyle.fill;

      canvas.save();
      canvas.translate(center.dx, center.dy);
      canvas.rotate(animation * 2 * math.pi);
      canvas.drawArc(
        Rect.fromCircle(center: const Offset(0, 0), radius: radius),
        0,
        math.pi / 2, // Radar wedge width
        true,
        scanArmPaint,
      );
      canvas.restore();
      
      // Progress line
      final arcPaint = Paint()
        ..color = primaryThemeColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 12
        ..strokeCap = StrokeCap.round;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        -math.pi / 2,
        sweepAngle,
        false,
        arcPaint,
      );
    } else if (state == ScanState.safe || state == ScanState.risk) {
      final resultPaint = Paint()
        ..color = primaryThemeColor.withValues(alpha: 0.8)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 6;
      canvas.drawCircle(center, radius, resultPaint);
    }
  }

  @override
  bool shouldRepaint(covariant ScannerPainter oldDelegate) => true;
}


