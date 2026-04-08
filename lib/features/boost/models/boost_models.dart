class BoostResponseData {
  final int memoryBeforeMb;
  final int memoryAfterMb;
  final int appsOptimized;
  final int performanceScore;
  final String message;

  BoostResponseData({
    required this.memoryBeforeMb,
    required this.memoryAfterMb,
    required this.appsOptimized,
    required this.performanceScore,
    required this.message,
  });

  factory BoostResponseData.fromJson(Map<String, dynamic> json) {
    return BoostResponseData(
      memoryBeforeMb: json['memory_before_mb'] ?? 0,
      memoryAfterMb: json['memory_after_mb'] ?? 0,
      appsOptimized: json['apps_optimized'] ?? 0,
      performanceScore: json['performance_score'] ?? 0,
      message: json['message'] ?? '',
    );
  }
}
