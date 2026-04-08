import 'package:flutter/material.dart';
import 'dart:math' as math;

class Responsive {
  static double width(BuildContext context) => MediaQuery.of(context).size.width;
  static double height(BuildContext context) => MediaQuery.of(context).size.height;

  static bool isSmallMobile(BuildContext context) => width(context) < 360;
  static bool isMobile(BuildContext context) => width(context) < 600;
  static bool isTablet(BuildContext context) => width(context) >= 600 && width(context) < 1024;
  static bool isDesktop(BuildContext context) => width(context) >= 1024;

  /// Scales a value based on the screen width relative to a baseline (375px)
  static double scale(BuildContext context, double baseSize) {
    double screenWidth = width(context);
    // Limit scaling factor to prevent massive text or invisible text
    double factor = math.min(math.max(screenWidth / 375.0, 0.85), 1.2);
    return baseSize * factor;
  }

  /// Scale specifically for extremely small screens (320px)
  static double scaleSmall(BuildContext context, double baseSize) {
    if (width(context) <= 320) {
      return baseSize * 0.9;
    }
    return baseSize;
  }
}
