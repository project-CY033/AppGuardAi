class ScanReport {
  final String id;
  final String appName;
  final String packageName;
  final String status; // 'Safe' or 'Risk'
  final int riskScore;
  final DateTime scanTime;
  final String iconPath;

  ScanReport({
    required this.id,
    required this.appName,
    required this.packageName,
    required this.status,
    required this.riskScore,
    required this.scanTime,
    this.iconPath = 'assets/logos/logo.png', // Default icon
  });
}
