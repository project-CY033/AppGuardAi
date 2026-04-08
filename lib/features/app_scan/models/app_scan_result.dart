enum RiskLevel { low, medium, high }

class AppScanResult {
  final String appName;
  final String packageName;
  final bool isSafe;
  final RiskLevel riskLevel;
  final int riskScore;
  final String description;
  final String? iconPath; // Optional mock icon path or byte data

  AppScanResult({
    required this.appName,
    required this.packageName,
    required this.isSafe,
    required this.riskLevel,
    required this.riskScore,
    required this.description,
    this.iconPath,
  });
}
