import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'dart:math' as math;
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/responsive_helper.dart';
import '../models/app_scan_result.dart';

class ScanProgressWidget extends StatelessWidget {
  final double progress;
  final String status;

  const ScanProgressWidget({
    super.key,
    required this.progress,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    double size = Responsive.isSmallMobile(context) ? 200 : math.min(Responsive.width(context) * 0.7, 280);

    return Column(
      children: [
        SizedBox(
          height: size,
          width: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Outer radar sweep
              Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: AppColors.primaryBlue.withValues(alpha: 0.1),
                    width: 2,
                  ),
                ),
              ),
              CustomPaint(
                size: Size(size, size),
                painter: _ProgressArcPainter(progress: progress),
              ).animate(onPlay: (c) => c.repeat()).rotate(duration: 2.seconds),
              
              // Inner text
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    "${progress.toInt()}%",
                    style: TextStyle(
                      fontSize: Responsive.isSmallMobile(context) ? 32 : 40,
                      fontWeight: FontWeight.w900,
                      color: AppColors.primaryBlue,
                    ),
                  ),
                  const Text(
                    "Scanning...",
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey,
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
          child: Text(
            status,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.textDark,
            ),
          ),
        ),
      ],
    );
  }
}

class _ProgressArcPainter extends CustomPainter {
  final double progress;

  _ProgressArcPainter({required this.progress});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;
    
    final sweepAngle = (progress / 100) * 2 * math.pi;
    final arcPaint = Paint()
      ..shader = const SweepGradient(
        colors: [Colors.transparent, AppColors.primaryBlue],
        stops: [0.7, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2, // Start at top
      sweepAngle,
      false,
      arcPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _ProgressArcPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

class AppScanCard extends StatelessWidget {
  final AppScanResult result;
  final VoidCallback onUninstall;
  final VoidCallback onIgnore;
  final bool isSelected;
  final ValueChanged<bool?>? onToggleSelect;

  const AppScanCard({
    super.key,
    required this.result,
    required this.onUninstall,
    required this.onIgnore,
    this.isSelected = false,
    this.onToggleSelect,
  });

  @override
  Widget build(BuildContext context) {
    bool isTiny = Responsive.isSmallMobile(context);
    Color statusColor = result.isSafe ? Colors.green : (result.riskLevel == RiskLevel.high ? Colors.redAccent : Colors.orange);
    IconData statusIcon = result.isSafe ? Icons.check_circle_outline : Icons.warning_amber_rounded;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isSelected ? Colors.redAccent.withValues(alpha: 0.05) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: isSelected ? Colors.redAccent : statusColor.withValues(alpha: 0.2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (!result.isSafe && onToggleSelect != null)
                Checkbox(
                  value: isSelected,
                  onChanged: onToggleSelect,
                  activeColor: Colors.redAccent,
                ),
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.primaryBlue.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: result.iconPath != null
                    ? Image.asset(result.iconPath!) // Assuming it's an asset for mock, or switch to memory image
                    : const Icon(Icons.android, color: AppColors.primaryBlue, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      result.appName,
                      style: TextStyle(
                        fontSize: isTiny ? 15 : 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textDark,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      result.packageName,
                      style: TextStyle(
                        fontSize: isTiny ? 11 : 12,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(statusIcon, color: statusColor, size: 14),
                        const SizedBox(width: 4),
                        Text(
                          result.isSafe 
                              ? "Safe" 
                              : (result.riskLevel == RiskLevel.high ? "High Risk" : "Medium Risk"),
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: statusColor,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            result.description,
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey[800],
            ),
          ),
          if (!result.isSafe) ...[
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: onIgnore,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.grey[700],
                      side: BorderSide(color: Colors.grey[300]!),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    child: const Text("Keep Anyway"),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: onUninstall,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.redAccent,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      elevation: 0,
                    ),
                    child: const Text("Uninstall"),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
