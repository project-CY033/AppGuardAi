import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../core/api/api_config.dart';
import 'models/boost_models.dart';

class BoostService {
  // Use a platform-aware base URL
  String get baseUrl => ApiConfig.baseUrl;

  Future<BoostResponseData> optimizeDevice({
    required int estimatedRamUsageMb,
    required int totalRamMb,
    required int backgroundAppsCount,
    required double storagePressurePercent,
    required double cpuUsagePercent,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConfig.boostUrl),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        "estimated_ram_usage_mb": estimatedRamUsageMb,
        "total_ram_mb": totalRamMb,
        "background_apps_count": backgroundAppsCount,
        "storage_pressure_percent": storagePressurePercent,
        "cpu_usage_percent": cpuUsagePercent,
      }),
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return BoostResponseData.fromJson(data);
    } else {
      throw Exception('Failed to optimize device: ${response.statusCode}');
    }
  }
}
