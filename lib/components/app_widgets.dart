import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../core/utils/responsive_helper.dart';

class FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final Color? iconColor;

  const FeatureCard({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        double padding = Responsive.isSmallMobile(context) ? 12 : 16;
        double iconSize = Responsive.isSmallMobile(context) ? 20 : 24;

        return GestureDetector(
          onTap: onTap,
          child: Container(
            padding: EdgeInsets.all(padding),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: (iconColor ?? AppColors.primaryBlue).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    icon,
                    color: iconColor ?? AppColors.primaryBlue,
                    size: iconSize,
                  ),
                ),
                const SizedBox(height: 8),
                Flexible(
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    alignment: Alignment.centerLeft,
                    child: Text(
                      title,
                      style: TextStyle(
                        fontSize: Responsive.scaleSmall(context, 15),
                        fontWeight: FontWeight.w700,
                        color: AppColors.textDark,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 2),
                Flexible(
                  child: Text(
                    subtitle,
                    maxLines: 2,
                    softWrap: true,
                    overflow: TextOverflow.visible,
                    style: TextStyle(
                      fontSize: Responsive.scaleSmall(context, 11),
                      color: AppColors.textDark.withValues(alpha: 0.5),
                      height: 1.1,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class DashboardHeader extends StatelessWidget {
  final String title;
  final VoidCallback? onSettingsTap;
  final VoidCallback? onNotificationTap;
  final int unreadCount;

  const DashboardHeader({
    super.key,
    required this.title,
    this.onSettingsTap,
    this.onNotificationTap,
    this.unreadCount = 0,
  });

  @override
  Widget build(BuildContext context) {
    bool isSmall = Responsive.isSmallMobile(context);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Flexible(
            child: Row(
              children: [
                Image.asset(
                  'assets/logos/logo.png',
                  height: isSmall ? 28 : 32,
                  width: isSmall ? 28 : 32,
                  fit: BoxFit.contain,
                ),
                const SizedBox(width: 10),
                Flexible(
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    child: RichText(
                      text: TextSpan(
                        style: TextStyle(
                          fontSize: isSmall ? 18 : 22,
                          fontWeight: FontWeight.w900,
                          fontFamily: 'Inter',
                        ),
                        children: const [
                          TextSpan(
                            text: "AppGuard",
                            style: TextStyle(color: AppColors.textDark),
                          ),
                          TextSpan(
                            text: "Ai",
                            style: TextStyle(color: AppColors.primaryBlue),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
                if (onNotificationTap != null)
                  Stack(
                    alignment: Alignment.topRight,
                    children: [
                      IconButton(
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        onPressed: onNotificationTap,
                        icon: Icon(
                          Icons.notifications_outlined,
                          color: AppColors.textDark,
                          size: isSmall ? 20 : 24,
                        ),
                      ),
                      if (unreadCount > 0)
                        Positioned(
                          right: 2,
                          top: 2,
                          child: Container(
                            padding: const EdgeInsets.all(2),
                            decoration: const BoxDecoration(
                              color: Colors.redAccent,
                              shape: BoxShape.circle,
                            ),
                            constraints: const BoxConstraints(
                              minWidth: 10,
                              minHeight: 10,
                            ),
                          ),
                        ),
                    ],
                  ),
                if (onSettingsTap != null) ...[
                  const SizedBox(width: 12),
                  IconButton(
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    onPressed: onSettingsTap,
                    icon: Icon(
                      Icons.settings_outlined,
                      color: AppColors.textDark,
                      size: isSmall ? 20 : 24,
                    ),
                  ),
                ],
              ],
            ),
        ],
      ),
    );
  }
}
