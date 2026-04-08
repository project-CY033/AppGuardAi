import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_native_splash/flutter_native_splash.dart';
import '../../core/theme/app_theme.dart';
import '../../app/routes.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  String _statusText = "";

  @override
  void initState() {
    super.initState();
    _startSequence();
  }

  Future<void> _startSequence() async {
    // ⏱ Timing Overview (Total ~4.2s):
    // 0.0s -> internal Init
    // 0.2s -> Flutter Native Splash removed
    // 0.0s -> Logo In (Animated)
    // 2.0s -> Status Text Change
    // 3.5s -> All Out (Final Fade)
    // 4.2s -> Navigate
    
    // Hold for a moment to ensure native splash is visible
    await Future.delayed(300.ms);
    FlutterNativeSplash.remove();

    // Logo + name animation chalne do
    await Future.delayed(1800.ms);
    if (mounted) {
      setState(() {
        _statusText = "Initializing AI Security Engine...";
      });
    }
    // Keep text visible (IMPORTANT)
    await Future.delayed(2000.ms);
    await Future.delayed(300.ms);
    if (mounted) {
      Navigator.pushReplacementNamed(context, AppRoutes.onboarding);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 🔹 Logo
            ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: Image.asset(
                "assets/logos/Applogo.png",
                width: 120,
                height: 120,
                fit: BoxFit.contain,
              ),
            )
            .animate()
            .fadeIn(duration: 800.ms)
            .scale(
              begin: const Offset(0.8, 0.8),
              end: const Offset(1.0, 1.0),
              duration: 800.ms,
              curve: Curves.easeOutBack,
            )
            .then(delay: 2500.ms)
            .fadeOut(duration: 700.ms),

            const SizedBox(height: 24),

            // 🔹 App Name
            RichText(
              text: const TextSpan(
                text: "AppGuard",
                style: TextStyle(
                  color: AppColors.textDark,
                  fontSize: 26,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                ),
                children: [
                  TextSpan(
                    text: "Ai",
                    style: TextStyle(
                      color: AppColors.primaryBlue,
                    ),
                  ),
                ],
              ),
            )
            .animate()
            .fadeIn(delay: 600.ms, duration: 600.ms)
            .moveY(begin: 15, end: 0, duration: 600.ms)
            .then(delay: 2100.ms)
            .fadeOut(duration: 700.ms),

            const SizedBox(height: 16),

            // 🔹 Status Text
            AnimatedOpacity(
              duration: 500.ms,
              opacity: _statusText.isNotEmpty ? 1.0 : 0.0,
              child: Text(
                _statusText,
                style: TextStyle(
                  color: AppColors.textDark.withValues(alpha: 0.6),
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            )
            .animate()
            .then(delay: 3300.ms)
            .fadeOut(duration: 700.ms),
          ],
        ),
      ),
    );
  }
}