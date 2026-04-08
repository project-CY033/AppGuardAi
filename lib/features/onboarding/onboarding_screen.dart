import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../components/app_button.dart';
import '../../core/theme/app_theme.dart';
import '../../core/utils/responsive_helper.dart';

class OnboardingScreen extends StatefulWidget {
  final VoidCallback onFinish;
  const OnboardingScreen({super.key, required this.onFinish});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _controller = PageController();
  int currentIndex = 0;

  final List<_OnboardingData> pages = [
    _OnboardingData(
      icon: Icons.shield_outlined,
      title: "Secure Your Device",
      subtitle: "Scan installed apps and detect hidden threats with our advanced AI engine.",
    ),
    _OnboardingData(
      icon: Icons.picture_as_pdf_outlined,
      title: "Analyze Files",
      subtitle: "Upload PDFs and detect malicious content instantly before they harm your system.",
    ),
    _OnboardingData(
      icon: Icons.security,
      title: "Real-Time Protection",
      subtitle: "Get live alerts and detailed security reports 24/7 to keep your data safe.",
    ),
  ];

  @override
  Widget build(BuildContext context) {
    bool isTiny = Responsive.isSmallMobile(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // 🔹 Skip Button
            Align(
              alignment: Alignment.topRight,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: InkWell(
                  onTap: widget.onFinish,
                  borderRadius: BorderRadius.circular(20),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppColors.textDark.withValues(alpha: 0.05),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      "Skip",
                      style: TextStyle(
                        color: AppColors.textDark.withValues(alpha: 0.6),
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              )
              .animate()
              .fadeIn(delay: 600.ms, duration: 400.ms)
              .moveX(begin: 20, end: 0, duration: 400.ms),
            ),

            // 🔹 Page View
            Expanded(
              child: PageView.builder(
                controller: _controller,
                itemCount: pages.length,
                onPageChanged: (index) {
                  setState(() => currentIndex = index);
                },
                itemBuilder: (context, index) {
                  final page = pages[index];
                  return Padding(
                    padding: EdgeInsets.symmetric(horizontal: isTiny ? 24 : 40),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Icon with Animation
                        Container(
                          padding: EdgeInsets.all(isTiny ? 24 : 32),
                          decoration: BoxDecoration(
                            color: AppColors.primaryBlue.withValues(alpha: 0.05),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            page.icon,
                            size: isTiny ? 60 : 80,
                            color: AppColors.primaryBlue,
                          ),
                        )
                        .animate(key: ValueKey("icon_$index"))
                        .fadeIn(duration: 600.ms)
                        .scale(begin: const Offset(0.7, 0.7), curve: Curves.easeOutBack, duration: 600.ms),

                        SizedBox(height: isTiny ? 32 : 48),

                        // Title
                        Text(
                          page.title,
                          style: TextStyle(
                            fontSize: Responsive.scale(context, 28),
                            fontWeight: FontWeight.w700,
                            color: AppColors.textDark,
                            letterSpacing: -0.5,
                            height: 1.1,
                          ),
                          textAlign: TextAlign.center,
                        )
                        .animate(key: ValueKey("title_$index"))
                        .fadeIn(delay: 200.ms, duration: 600.ms)
                        .moveY(begin: 10, end: 0, duration: 600.ms),

                        const SizedBox(height: 16),

                        // Subtitle
                        Text(
                          page.subtitle,
                          style: TextStyle(
                            fontSize: isTiny ? 14 : 16,
                            height: 1.4,
                            color: AppColors.textDark.withValues(alpha: 0.6),
                          ),
                          textAlign: TextAlign.center,
                        )
                        .animate(key: ValueKey("subtitle_$index"))
                        .fadeIn(delay: 400.ms, duration: 600.ms)
                        .moveY(begin: 10, end: 0, duration: 600.ms),
                      ],
                    ),
                  );
                },
              ),
            ),

            // 🔹 Footer Area
            Padding(
              padding: EdgeInsets.fromLTRB(32, 16, 32, isTiny ? 24 : 32),
              child: Column(
                children: [
                  // Indicator Dots
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(
                      pages.length,
                      (index) => AnimatedContainer(
                        duration: 300.ms,
                        margin: const EdgeInsets.symmetric(horizontal: 4),
                        height: 8,
                        width: currentIndex == index ? 24 : 8,
                        decoration: BoxDecoration(
                          color: currentIndex == index
                              ? AppColors.primaryBlue
                              : AppColors.textDark.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                  ),

                  SizedBox(height: isTiny ? 24 : 32),

                  // Action Button
                  AppButton(
                    title: currentIndex == pages.length - 1
                        ? "Get Started"
                        : "Next Step",
                    onPressed: () {
                      if (currentIndex == pages.length - 1) {
                        widget.onFinish();
                      } else {
                        _controller.nextPage(
                          duration: 400.ms,
                          curve: Curves.easeInOut,
                        );
                      }
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _OnboardingData {
  final IconData icon;
  final String title;
  final String subtitle;

  _OnboardingData({
    required this.icon,
    required this.title,
    required this.subtitle,
  });
}