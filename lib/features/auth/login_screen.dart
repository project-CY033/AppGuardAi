import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../core/theme/app_theme.dart';
import '../../components/app_button.dart';
import '../../components/app_input.dart';
import '../../app/routes.dart';
import '../../core/utils/responsive_helper.dart';

class LoginScreen extends StatefulWidget {
  final VoidCallback onLogin;
  const LoginScreen({super.key, required this.onLogin});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool rememberMe = false;
  bool obscurePassword = true;

  final emailCtrl = TextEditingController();
  final passCtrl = TextEditingController();

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
                        top: MediaQuery.of(context).padding.top + (isTiny ? 20 : 40),
                        bottom: isTiny ? 40 : 60,
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
                                  height: isTiny ? 50 : 64,
                                  width: isTiny ? 50 : 64,
                                  fit: BoxFit.contain,
                                ),
                              )
                              .animate()
                              .fadeIn(duration: 800.ms)
                              .scale(begin: const Offset(0.8, 0.8), curve: Curves.easeOutBack),

                              const SizedBox(height: 16),

                              Text(
                                "Login Now",
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: Responsive.scale(context, 26),
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
                                  "Enter your email and password to log in",
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
                                SizedBox(height: isTiny ? 30 : 40),
                                
                                AppInput(
                                  controller: emailCtrl,
                                  hintText: "Enter your email",
                                  keyboardType: TextInputType.emailAddress,
                                )
                                .animate()
                                .fadeIn(delay: 600.ms, duration: 600.ms),

                                const SizedBox(height: 16),

                                AppInput(
                                  controller: passCtrl,
                                  hintText: "Enter your password",
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
                                .fadeIn(delay: 700.ms, duration: 600.ms),

                                const SizedBox(height: 16),

                                Row(
                                  children: [
                                    SizedBox(
                                      height: 18,
                                      width: 18,
                                      child: Checkbox(
                                        value: rememberMe,
                                        activeColor: AppColors.primaryBlue,
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                        onChanged: (v) => setState(() => rememberMe = v ?? false),
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      "Remember me",
                                      style: TextStyle(
                                        color: AppColors.textDark.withValues(alpha: 0.8),
                                        fontSize: 12,
                                      ),
                                    ),
                                    const Spacer(),
                                    Flexible(
                                      child: TextButton(
                                        onPressed: () => Navigator.pushNamed(context, AppRoutes.forgotPassword),
                                        style: TextButton.styleFrom(
                                          padding: EdgeInsets.zero,
                                          minimumSize: const Size(0, 0),
                                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                        ),
                                        child: const Text(
                                          "Forgot Password?",
                                          overflow: TextOverflow.ellipsis,
                                          style: TextStyle(
                                            color: AppColors.primaryBlue,
                                            fontSize: 12,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                )
                                .animate()
                                .fadeIn(delay: 800.ms, duration: 600.ms),

                                const SizedBox(height: 24),

                                AppButton(
                                  title: "Log In",
                                  onPressed: widget.onLogin,
                                )
                                .animate()
                                .fadeIn(delay: 900.ms, duration: 600.ms),

                                const SizedBox(height: 24),

                                Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      "Don't have an account? ",
                                      style: TextStyle(
                                        color: AppColors.textLight.withValues(alpha: 0.8),
                                        fontSize: 13,
                                      ),
                                    ),
                                    GestureDetector(
                                      onTap: () => Navigator.pushNamed(context, AppRoutes.signup),
                                      child: const Text(
                                        "Sign Up",
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
                                .fadeIn(delay: 1000.ms, duration: 600.ms),
                                
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