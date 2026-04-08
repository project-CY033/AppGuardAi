import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/responsive_helper.dart';
import '../models/pdf_scan_report.dart';
import '../pdf_scan_controller.dart';
class PdfUploadCard extends StatelessWidget {
  final String? fileName;
  final String? fileSize;
  final VoidCallback onTap;

  const PdfUploadCard({
    super.key,
    this.fileName,
    this.fileSize,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    bool isTiny = Responsive.isSmallMobile(context);
    bool hasFile = fileName != null;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.all(isTiny ? 24 : 32),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: AppColors.primaryBlue.withValues(alpha: 0.2),
            width: 2,
            style: BorderStyle.solid,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.primaryBlue.withValues(alpha: 0.05),
                shape: BoxShape.circle,
              ),
              child: Icon(
                hasFile ? Icons.description_rounded : Icons.cloud_upload_outlined,
                size: isTiny ? 40 : 48,
                color: AppColors.primaryBlue,
              ),
            ),
            const SizedBox(height: 20),
            Text(
              hasFile ? fileName! : "Upload PDF Document",
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textDark,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              hasFile ? fileSize! : "Tap to select a PDF file for security analysis",
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textDark.withValues(alpha: 0.5),
              ),
            ),
            if (!hasFile) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: BoxDecoration(
                  color: AppColors.primaryBlue,
                  borderRadius: BorderRadius.circular(30),
                ),
                child: const Text(
                  "Choose File",
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class PdfScanningView extends StatelessWidget {
  final double progress;
  final String status;

  const PdfScanningView({
    super.key,
    required this.progress,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    bool isTiny = Responsive.isSmallMobile(context);
    double size = isTiny ? 180 : 220;

    return Column(
      children: [
        SizedBox(
          height: size,
          width: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Rotating Gradient Border
              RotationTransition(
                turns: const AlwaysStoppedAnimation(0.5),
                child: Container(
                  width: size,
                  height: size,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: SweepGradient(
                      colors: [Colors.transparent, AppColors.primaryBlue],
                      stops: const [0.7, 1.0],
                    ),
                  ),
                ),
              ).animate(onPlay: (c) => c.repeat()).rotate(duration: 2.seconds),
              
              // Inner Background
              Container(
                width: size - 8,
                height: size - 8,
                decoration: const BoxDecoration(
                  color: AppColors.background,
                  shape: BoxShape.circle,
                ),
              ),

              // Percentage
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    "${progress.toInt()}%",
                    style: TextStyle(
                      fontSize: isTiny ? 36 : 48,
                      fontWeight: FontWeight.w900,
                      color: AppColors.primaryBlue,
                    ),
                  ),
                  Text(
                    "Analyzing",
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textDark.withValues(alpha: 0.6),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 40),
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
          ).animate(onPlay: (c) => c.repeat(reverse: true)).fadeIn(duration: 800.ms),
        ),
      ],
    );
  }
}

class PdfResultPanel extends StatelessWidget {
  final PdfScanReport report;
  final VoidCallback onReset;

  const PdfResultPanel({
    super.key,
    required this.report,
    required this.onReset,
  });

  @override
  Widget build(BuildContext context) {
    bool isRisk = report.scanScore < 70;
    bool isTiny = Responsive.isSmallMobile(context);

    return Column(
      children: [
        // Result Summary Header
        Container(
          padding: EdgeInsets.all(isTiny ? 20 : 24),
          decoration: BoxDecoration(
            color: (isRisk ? Colors.redAccent : Colors.greenAccent).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(
              color: (isRisk ? Colors.redAccent : Colors.greenAccent).withValues(alpha: 0.2),
            ),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isRisk ? Colors.redAccent : Colors.greenAccent,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  isRisk ? Icons.warning_rounded : Icons.check_circle_rounded,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isRisk ? "Potential Risk Detected" : "Safe – No threats detected",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: isRisk ? Colors.red[700] : Colors.green[700],
                      ),
                    ),
                    Text(
                      "Security Score: ${report.scanScore}%",
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textDark.withValues(alpha: 0.6),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ).animate().fadeIn().slideY(begin: 0.1, end: 0),

        const SizedBox(height: 32),

        // Checks List
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: report.checks.length,
          itemBuilder: (context, index) {
            final check = report.checks[index];
            return _PdfCheckItem(check: check).animate(delay: (index * 100).ms).fadeIn().slideX(begin: 0.05, end: 0);
          },
        ),

        const SizedBox(height: 32),

        // Action Buttons
        Row(
          children: [
            Expanded(
              child: ElevatedButton(
                onPressed: () => context.read<PdfScanController>().deletePdf(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.redAccent,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 0,
                ),
                child: const Text(
                  "Delete File",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: OutlinedButton(
                onPressed: () => context.read<PdfScanController>().keepPdf(),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  foregroundColor: AppColors.textDark.withValues(alpha: 0.7),
                  side: BorderSide(color: AppColors.textDark.withValues(alpha: 0.2)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                child: const Text("Keep Anyway"),
              ),
            ),
          ],
        ).animate(delay: 600.ms).fadeIn(),
        
        const SizedBox(height: 16),
        TextButton(
          onPressed: onReset,
          child: const Text("Scan Another Document", style: TextStyle(color: AppColors.primaryBlue)),
        ),
      ],
    );
  }
}

class _PdfCheckItem extends StatelessWidget {
  final PdfCheck check;

  const _PdfCheckItem({required this.check});

  @override
  Widget build(BuildContext context) {
    Color statusColor = Colors.grey;
    IconData statusIcon = Icons.help_outline;

    switch (check.status) {
      case PdfCheckStatus.safe:
        statusColor = Colors.green;
        statusIcon = Icons.check_circle_outline;
        break;
      case PdfCheckStatus.warning:
        statusColor = Colors.orange;
        statusIcon = Icons.error_outline;
        break;
      case PdfCheckStatus.risk:
        statusColor = Colors.red;
        statusIcon = Icons.dangerous_outlined;
        break;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.02), blurRadius: 4, offset: const Offset(0, 2)),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(statusIcon, color: statusColor, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  check.title,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                ),
                const SizedBox(height: 4),
                Text(
                  check.description,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textDark.withValues(alpha: 0.5),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Text(
            check.status.name.toUpperCase(),
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w900,
              color: statusColor,
            ),
          ),
        ],
      ),
    );
  }
}
