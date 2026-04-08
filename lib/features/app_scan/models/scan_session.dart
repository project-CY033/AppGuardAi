class ScanSession {
  final int totalAppsScanned;
  final int safeAppsCount;
  final int riskyAppsCount;
  final int overallSecurityScore; // Percentage 0-100

  ScanSession({
    required this.totalAppsScanned,
    required this.safeAppsCount,
    required this.riskyAppsCount,
    required this.overallSecurityScore,
  });
}
