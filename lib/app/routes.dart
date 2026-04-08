import 'package:flutter/material.dart';
import '../features/splash/splash_screen.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/signup_screen.dart';
import '../features/auth/forgotpassword_screeen.dart';
import '../features/dashboard/dashboard.dart';

import '../features/reports/reports_screen.dart';
import '../features/pdf_scan/pdf_scan_screen.dart';
import '../features/app_scan/app_scan_screen.dart';
import '../features/notifications/notifications_screen.dart';
import '../features/settings/settings_screen.dart';
import '../features/deep_clean/deep_clean_screen.dart';
import '../features/boost/boost_speed_screen.dart';
import '../features/manage_apps/manage_apps_screen.dart';
import '../features/manage_apps/app_info_screen.dart';
import '../features/manage_apps/manage_apps_controller.dart';

class AppRoutes {
  static const String splash = '/';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String forgotPassword = '/forgot-password';
  static const String dashboard = '/dashboard';
  static const String reports = '/reports';
  static const String pdfScan = '/pdf-scan';
  static const String appScan = '/app-scan';
  static const String notifications = '/notifications';
  static const String settings = '/settings';
  static const String deepClean = '/deep-clean';
  static const String boostSpeed = '/boost-speed';
  static const String manageApps = '/manage-apps';
  static const String appInfo = '/app-info';

  static Map<String, WidgetBuilder> get routes => {
    splash: (context) => const SplashScreen(),
    onboarding: (context) => OnboardingScreen(
      onFinish: () => Navigator.pushReplacementNamed(context, login),
    ),
    login: (context) => LoginScreen(
      onLogin: () => Navigator.pushReplacementNamed(context, dashboard),
    ),
    signup: (context) => const SignUpScreen(),
    forgotPassword: (context) => const ForgotPasswordScreen(),
    dashboard: (context) => const DashboardScreen(),
    reports: (context) => const ReportsScreen(),
    pdfScan: (context) => const PdfScanScreen(),
    appScan: (context) => const AppScanScreen(),
    notifications: (context) => const NotificationsScreen(),
    settings: (context) => const SettingsScreen(),
    deepClean: (context) => const DeepCleanScreen(),
    boostSpeed: (context) => const BoostSpeedScreen(),
    manageApps: (context) => const ManageAppsScreen(),
    appInfo: (context) {
      final args = ModalRoute.of(context)!.settings.arguments as MockAppDetails;
      return AppInfoScreen(appDetails: args);
    },
  };
}
