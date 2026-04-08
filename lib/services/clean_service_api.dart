import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api/api_config.dart';
import '../features/deep_clean/models/clean_models.dart';

class CleanServiceAPI {
  // Ideally this url should be pulled from a common base URL config
  static String get baseUrl => ApiConfig.cleanUrl;

  Future<CleanResponseData> analyzeStorage({
    required int totalSpaceBytes,
    required int usedSpaceBytes,
    required int installedAppsCount,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/analyze'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        "total_space_bytes": totalSpaceBytes,
        "used_space_bytes": usedSpaceBytes,
        "installed_apps_count": installedAppsCount,
      }),
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      return CleanResponseData.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to analyze storage: ${response.statusCode}');
    }
  }
}
