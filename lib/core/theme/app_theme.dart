import 'package:flutter/material.dart';

class AppColors {
  static const Color primaryBlue = Color(0xFF3283EC);
  static const Color primaryDark = Color(0xFF1E4CAF);
  static const Color background = Color(0xFFFAFAFA);
  static const Color backgroundLight = Color(0xFFF4F6FA);
  static const Color textDark = Color(0xFF1F2937); // Gray-800
  static const Color textLight = Color(0xFF6B7280); // Gray-500
  static const Color inputFill = Color(0xFFF4F6FA);
  static const Color secondaryGreen = Color(0xFF10B981); // Emerald-500
  static const Color backgroundDark = Color(0xFF1E293B); // Slate-800

  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF3A6FE8), Color(0xFF2F5DD6)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient horizontalGradient = LinearGradient(
    colors: [Color(0xFF3283EC), Color(0xFF1E4CAF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      scaffoldBackgroundColor: AppColors.background,
      primaryColor: AppColors.primaryBlue,
      fontFamily: 'Inter', // Assuming Inter is available or default
    );
  }
}
