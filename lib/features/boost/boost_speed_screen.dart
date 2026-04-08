import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import 'boost_controller.dart';
import 'widgets/rocket_animation.dart';

class BoostSpeedScreen extends StatefulWidget {
  const BoostSpeedScreen({super.key});

  @override
  State<BoostSpeedScreen> createState() => _BoostSpeedScreenState();
}

class _BoostSpeedScreenState extends State<BoostSpeedScreen> {
  final BoostController _controller = BoostController();

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onStateChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_onStateChanged);
    _controller.dispose();
    super.dispose();
  }

  void _onStateChanged() {
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text("Boost Speed", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: AppColors.textDark,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              minHeight: MediaQuery.of(context).size.height - kToolbarHeight - MediaQuery.of(context).padding.top - MediaQuery.of(context).padding.bottom,
            ),
            child: IntrinsicHeight(
              child: Column(
                children: [
                  // Header stats
                  if (_controller.state != BoostState.result)
                    Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _StatCounter("Memory", "${_controller.currentRamUsageMb} MB"),
                          _StatCounter("Apps", "${_controller.backgroundApps}"),
                        ],
                      ),
                    ),

                   const Spacer(),

                  // Animation Zone
                  SizedBox(
                    height: 350,
                    child: Stack(
                      alignment: Alignment.center,
                      clipBehavior: Clip.none,
                      children: [
                         RocketAnimation(
                           isAnimating: _controller.state == BoostState.animating,
                           isResult: _controller.state == BoostState.result,
                         ),
                         if (_controller.state == BoostState.animating)
                           Positioned(
                             bottom: 20,
                             child: Text(
                               '${_controller.progress.toInt()}%',
                               style: const TextStyle(
                                 color: AppColors.textDark,
                                 fontSize: 24,
                                 fontWeight: FontWeight.bold,
                               ),
                             ),
                           ),
                      ],
                    ),
                  ),

                  const Spacer(),

                  // Dynamic Messages & Controls
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        AnimatedSwitcher(
                          duration: const Duration(milliseconds: 300),
                          child: Text(
                            _controller.currentMessage,
                            key: ValueKey(_controller.currentMessage),
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: _controller.state == BoostState.result ? Colors.green.shade700 : AppColors.textDark,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                        const SizedBox(height: 32),
                        
                        if (_controller.state == BoostState.idle)
                          ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.primaryBlue,
                              foregroundColor: Colors.white,
                              minimumSize: const Size(double.infinity, 56),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                              elevation: 8,
                            ),
                            onPressed: () => _controller.startBoost(context),
                            child: const Text("BOOST NOW 🚀", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                          )
                        else if (_controller.state == BoostState.result)
                          _buildResultCard(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildResultCard() {
    final result = _controller.resultData;
    if (result == null) return const SizedBox();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          )
        ],
      ),
      child: Column(
        children: [
           Row(
             mainAxisAlignment: MainAxisAlignment.spaceBetween,
             children: [
               Text("Memory Freed:", style: TextStyle(color: AppColors.textDark.withValues(alpha: 0.7), fontSize: 16)),
               Text("${result.memoryBeforeMb - result.memoryAfterMb} MB", style: TextStyle(color: Colors.green.shade700, fontSize: 16, fontWeight: FontWeight.bold)),
             ],
           ),
           const SizedBox(height: 12),
           Row(
             mainAxisAlignment: MainAxisAlignment.spaceBetween,
             children: [
               Text("Apps Optimized:", style: TextStyle(color: AppColors.textDark.withValues(alpha: 0.7), fontSize: 16)),
               Text("${result.appsOptimized}", style: const TextStyle(color: AppColors.primaryBlue, fontSize: 16, fontWeight: FontWeight.bold)),
             ],
           ),
           const SizedBox(height: 12),
           Row(
             mainAxisAlignment: MainAxisAlignment.spaceBetween,
             children: [
               Text("Performance Score:", style: TextStyle(color: AppColors.textDark.withValues(alpha: 0.7), fontSize: 16)),
               Text("${result.performanceScore}/100", style: const TextStyle(color: Colors.orange, fontSize: 16, fontWeight: FontWeight.bold)),
             ],
           ),
           const SizedBox(height: 24),
           OutlinedButton(
             style: OutlinedButton.styleFrom(
               foregroundColor: AppColors.primaryBlue,
               side: const BorderSide(color: AppColors.primaryBlue),
               minimumSize: const Size(double.infinity, 50),
               shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
             ),
             onPressed: () {
               // Usually back to dashboard
               Navigator.pop(context);
             },
             child: const Text("Done"),
           ),
        ],
      ),
    );
  }
}

class _StatCounter extends StatelessWidget {
  final String label;
  final String value;
  
  const _StatCounter(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: const TextStyle(color: AppColors.textDark, fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(color: AppColors.textDark.withValues(alpha: 0.6), fontSize: 14)),
      ],
    );
  }
}
