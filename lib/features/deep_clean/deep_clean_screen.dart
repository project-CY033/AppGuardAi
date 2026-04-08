import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import 'deep_clean_controller.dart';

class DeepCleanScreen extends StatefulWidget {
  const DeepCleanScreen({super.key});

  @override
  State<DeepCleanScreen> createState() => _DeepCleanScreenState();
}

class _DeepCleanScreenState extends State<DeepCleanScreen> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
       vsync: this,
       duration: const Duration(seconds: 3),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  String _formatBytes(int bytes) {
    if (bytes <= 0) return "0 B";
    const suffixes = ["B", "KB", "MB", "GB", "TB"];
    var i = (math.log(bytes) / math.log(1024)).floor();
    return '${(bytes / math.pow(1024, i)).toStringAsFixed(2)} ${suffixes[i]}';
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => DeepCleanController(),
      child: Consumer<DeepCleanController>(
        builder: (context, controller, child) {
          
          if (controller.state == CleanState.scanning || controller.state == CleanState.cleaning) {
            if (!_animationController.isAnimating) _animationController.repeat();
          } else {
            _animationController.stop();
          }

          return Scaffold(
            backgroundColor: AppColors.background,
            appBar: AppBar(
              backgroundColor: Colors.transparent,
              elevation: 0,
              iconTheme: const IconThemeData(color: AppColors.textDark),
              title: const Text("Deep Clean", style: TextStyle(color: AppColors.textDark, fontWeight: FontWeight.bold)),
              actions: [
                if (controller.state == CleanState.success || controller.state == CleanState.results)
                  IconButton(icon: const Icon(Icons.refresh), onPressed: controller.reset),
              ],
            ),
            body: SafeArea(
              child: Column(
                children: [
                  _buildStorageBar(controller),
                  Expanded(
                    child: AnimatedSwitcher(
                      duration: const Duration(milliseconds: 500),
                      child: _buildBodyContent(controller),
                    ),
                  ),
                  if (controller.state == CleanState.results && controller.categories.isNotEmpty)
                    _buildCleanButton(controller),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildStorageBar(DeepCleanController controller) {
    final double usedRatio = controller.usedDeviceSpaceBytes / controller.totalDeviceSpaceBytes;
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text("Internal Storage", style: TextStyle(color: Colors.grey.shade600, fontWeight: FontWeight.w600)),
              Text("${_formatBytes(controller.usedDeviceSpaceBytes).split(' ')[0]} / ${_formatBytes(controller.totalDeviceSpaceBytes)}", 
                style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textDark)),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child:   Container(
                height: 12,
                width: double.infinity,
                color: Colors.grey.shade300,
                child: Row(
                  children: [
                    Flexible(
                      flex: (usedRatio * 100).toInt(),
                      child: Container(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [AppColors.primaryBlue, AppColors.primaryBlue.withValues(alpha: 0.7)]
                          )
                        ),
                      ),
                    ),
                    Flexible(
                      flex: 100 - (usedRatio * 100).toInt(),
                      child: Container(color: Colors.transparent),
                    )
                  ],
                ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBodyContent(DeepCleanController controller) {
    switch (controller.state) {
      case CleanState.idle:
        return _buildIdleState(controller);
      case CleanState.scanning:
      case CleanState.cleaning:
        return _buildScanningState(controller);
      case CleanState.results:
        return _buildResultsState(controller);
      case CleanState.success:
        return _buildSuccessState(controller);
    }
  }

  Widget _buildIdleState(DeepCleanController controller) {
    return Center(
      key: const ValueKey('idle'),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.cleaning_services_rounded, size: 80, color: AppColors.primaryBlue.withValues(alpha: 0.8)),
          const SizedBox(height: 24),
          const Text("Optimize your storage", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.textDark)),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text("Scan for junk files, residual data, and app cache to free up space securely.", 
              textAlign: TextAlign.center, style: TextStyle(fontSize: 14, color: Colors.grey.shade600)),
          ),
          const SizedBox(height: 48),
          ElevatedButton(
            onPressed: () => controller.startScan(),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primaryBlue,
              padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              elevation: 4,
            ),
            child: const Text("START SCAN", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white, letterSpacing: 1.2)),
          )
        ],
      ),
    );
  }

  Widget _buildScanningState(DeepCleanController controller) {
    bool isCleaning = controller.state == CleanState.cleaning;
    Color radarColor = isCleaning ? Colors.green : AppColors.primaryBlue;

    return Center(
      key: ValueKey(isCleaning ? 'cleaning' : 'scanning'),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 240, height: 240,
            child: Stack(
              alignment: Alignment.center,
              children: [
                AnimatedBuilder(
                  animation: _animationController,
                  builder: (context, child) {
                    return CustomPaint(
                      painter: CleanRadarPainter(
                        animation: _animationController.value,
                        progress: controller.progress,
                        baseColor: radarColor,
                      ),
                      child: Container(),
                    );
                  }
                ),
                Text(
                  "${controller.progress.toInt()}%",
                  style: TextStyle(fontSize: 48, fontWeight: FontWeight.w900, color: radarColor),
                ),
              ],
            )
          ),
          const SizedBox(height: 40),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Text(
              controller.statusMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textDark),
            ),
          )
        ],
      ),
    );
  }

  Widget _buildResultsState(DeepCleanController controller) {
    if (controller.categories.isEmpty) {
      return const Center(child: Text("Device is already optimized!"));
    }

    return Column(
      key: const ValueKey('results'),
      children: [
        Padding(
          padding: const EdgeInsets.all(24.0),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
            decoration: BoxDecoration(
              color: Colors.orange.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
            ),
            child: Column(
              children: [
                const Text("Junk Found", style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 8),
                Text(
                  _formatBytes(controller.selectedCleanableBytes),
                  style: const TextStyle(fontSize: 42, fontWeight: FontWeight.w900, color: AppColors.textDark),
                ),
                const SizedBox(height: 8),
                Text("can be safely removed", style: TextStyle(color: Colors.grey.shade700, fontSize: 13)),
              ],
            ),
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: controller.categories.length,
            itemBuilder: (context, index) {
              final cat = controller.categories[index];
              return Card(
                elevation: 0,
                color: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                margin: const EdgeInsets.symmetric(vertical: 6),
                child: CheckboxListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  activeColor: AppColors.primaryBlue,
                  title: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(cat.category, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      Text(_formatBytes(cat.sizeBytes), style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primaryBlue)),
                    ],
                  ),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 6.0),
                    child: Text(cat.description, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                  ),
                  value: cat.isSelected,
                  onChanged: (val) => controller.toggleCategory(cat.id),
                ),
              );
            },
          ),
        )
      ],
    );
  }

  Widget _buildCleanButton(DeepCleanController controller) {
    bool canClean = controller.selectedCleanableBytes > 0;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10, offset: const Offset(0, -5))]
      ),
      child: SafeArea(
        child: SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: canClean ? () => controller.cleanSelected() : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: canClean ? AppColors.primaryBlue : Colors.grey.shade300,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              elevation: canClean ? 4 : 0,
            ),
            child: Text(
              "CLEAN UP ${_formatBytes(controller.selectedCleanableBytes)}",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: canClean ? Colors.white : Colors.grey.shade600),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSuccessState(DeepCleanController controller) {
    return Center(
      key: const ValueKey('success'),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.green.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.check_circle_rounded, size: 80, color: Colors.green),
          ),
          const SizedBox(height: 32),
          const Text("Device Optimized!", style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textDark)),
          const SizedBox(height: 16),
          Text(
            "Freed ${_formatBytes(controller.freedBytes)}",
            style: const TextStyle(fontSize: 18, color: Colors.green, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 48),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
            ),
            child: const Text("DONE", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
          )
        ],
      ),
    );
  }
}

class CleanRadarPainter extends CustomPainter {
  final double animation;
  final double progress;
  final Color baseColor;

  CleanRadarPainter({required this.animation, required this.progress, required this.baseColor});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;

    final bgPaint = Paint()
      ..color = baseColor.withValues(alpha: 0.05)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, radius, bgPaint);

    final trackPaint = Paint()
      ..color = baseColor.withValues(alpha: 0.1)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8;
    canvas.drawCircle(center, radius, trackPaint);

    final sweepAngle = (progress / 100) * 2 * math.pi;
    final arcPaint = Paint()
      ..color = baseColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(Rect.fromCircle(center: center, radius: radius), -math.pi / 2, sweepAngle, false, arcPaint);
    
    final scannerPaint = Paint()
      ..shader = SweepGradient(
        colors: [baseColor.withValues(alpha: 0.0), baseColor.withValues(alpha: 0.6)],
        stops: const [0.5, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.fill;

    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(animation * 2 * math.pi);
    canvas.drawArc(Rect.fromCircle(center: const Offset(0, 0), radius: radius), 0, math.pi / 2, true, scannerPaint);
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant CleanRadarPainter oldDelegate) => true;
}
