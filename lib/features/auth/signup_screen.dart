import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../core/theme/app_theme.dart';
import '../../components/app_button.dart';
import '../../components/app_input.dart';
import '../../core/utils/responsive_helper.dart';

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final nameCtrl = TextEditingController();
  final mobileCtrl = TextEditingController();
  final emailCtrl = TextEditingController();
  final passCtrl = TextEditingController();
  final confirmPassCtrl = TextEditingController();
  
  bool obscurePassword = true;
  bool obscureConfirmPassword = true;

  @override
  Widget build(BuildContext context) {
    bool isTiny = Responsive.isSmallMobile(context);

    return Scaffold(
      backgroundColor: Colors.white,
      body: LayoutBuilder(
        builder: (context, constraints) {
          return SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: constraints.maxHeight,
              ),
              child: IntrinsicHeight(
                child: Column(
                  children: [
                    // 🔵 TOP GRADIENT SECTION
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.only(
                        top: MediaQuery.of(context).padding.top + (isTiny ? 20 : 30),
                        bottom: isTiny ? 30 : 50,
                      ),
                      decoration: const BoxDecoration(
                        gradient: AppColors.primaryGradient,
                      ),
                      child: Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 450),
                          child: Column(
                            children: [
                              // App Logo
                              Container(
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(16),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withValues(alpha: 0.1),
                                      blurRadius: 10,
                                      offset: const Offset(0, 4),
                                    ),
                                  ],
                                ),
                                clipBehavior: Clip.antiAlias,
                                child: Image.asset(
                                  'assets/logos/logo.png',
                                  height: isTiny ? 44 : 54,
                                  width: isTiny ? 44 : 54,
                                  fit: BoxFit.contain,
                                ),
                              )
                              .animate()
                              .fadeIn(duration: 800.ms)
                              .scale(begin: const Offset(0.8, 0.8), curve: Curves.easeOutBack),

                              const SizedBox(height: 12),

                              Text(
                                "Create Account",
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: Responsive.scale(context, 24),
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.5,
                                ),
                              )
                              .animate()
                              .fadeIn(delay: 200.ms, duration: 800.ms)
                              .moveY(begin: 10, end: 0),

                              const SizedBox(height: 8),

                              Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 24),
                                child: Text(
                                  "Join AppGuardAI to secure your apps",
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    color: Colors.white.withValues(alpha: 0.7),
                                    fontSize: isTiny ? 12 : 14,
                                  ),
                                ),
                              )
                              .animate()
                              .fadeIn(delay: 400.ms, duration: 800.ms)
                              .moveY(begin: 10, end: 0),
                            ],
                          ),
                        ),
                      ),
                    ),

                    // ⚪ WHITE CONTENT SECTION
                    Expanded(
                      child: Container(
                        width: double.infinity,
                        transform: Matrix4.translationValues(0, -20, 0),
                        padding: const EdgeInsets.fromLTRB(24, 0, 24, 20),
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.vertical(
                            top: Radius.circular(32),
                          ),
                        ),
                        child: Center(
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 400),
                            child: Column(
                              children: [
                                SizedBox(height: isTiny ? 24 : 34),
                                
                                AppInput(
                                  controller: nameCtrl,
                                  hintText: "Full Name",
                                  keyboardType: TextInputType.name,
                                )
                                .animate()
                                .fadeIn(delay: 500.ms, duration: 600.ms),

                                const SizedBox(height: 12),

                                AppInput(
                                  controller: mobileCtrl,
                                  hintText: "Mobile Number",
                                  keyboardType: TextInputType.phone,
                                )
                                .animate()
                                .fadeIn(delay: 600.ms, duration: 600.ms),

                                const SizedBox(height: 12),

                                AppInput(
                                  controller: emailCtrl,
                                  hintText: "Email Address",
                                  keyboardType: TextInputType.emailAddress,
                                )
                                .animate()
                                .fadeIn(delay: 700.ms, duration: 600.ms),

                                const SizedBox(height: 12),

                                AppInput(
                                  controller: passCtrl,
                                  hintText: "Password",
                                  obscureText: obscurePassword,
                                  suffixIcon: IconButton(
                                    icon: Icon(
                                      obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                      color: AppColors.textLight,
                                      size: 18,
                                    ),
                                    onPressed: () => setState(() => obscurePassword = !obscurePassword),
                                  ),
                                )
                                .animate()
                                .fadeIn(delay: 800.ms, duration: 600.ms),

                                const SizedBox(height: 12),

                                AppInput(
                                  controller: confirmPassCtrl,
                                  hintText: "Confirm Password",
                                  obscureText: obscureConfirmPassword,
                                  suffixIcon: IconButton(
                                    icon: Icon(
                                      obscureConfirmPassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                      color: AppColors.textLight,
                                      size: 18,
                                    ),
                                    onPressed: () => setState(() => obscureConfirmPassword = !obscureConfirmPassword),
                                  ),
                                )
                                .animate()
                                .fadeIn(delay: 900.ms, duration: 600.ms),

                                const SizedBox(height: 24),

                                AppButton(
                                  title: "Sign Up",
                                  onPressed: () {},
                                )
                                .animate()
                                .fadeIn(delay: 1000.ms, duration: 600.ms),

                                const SizedBox(height: 24),

                                Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      "Already have an account? ",
                                      style: TextStyle(
                                        color: AppColors.textLight.withValues(alpha: 0.8),
                                        fontSize: 13,
                                      ),
                                    ),
                                    GestureDetector(
                                      onTap: () => Navigator.pop(context),
                                      child: const Text(
                                        "Login",
                                        style: TextStyle(
                                          color: AppColors.primaryBlue,
                                          fontWeight: FontWeight.w700,
                                          fontSize: 13,
                                        ),
                                      ),
                                    ),
                                  ],
                                )
                                .animate()
                                .fadeIn(delay: 1100.ms, duration: 600.ms),
                                
                                const SizedBox(height: 20),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
