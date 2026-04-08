import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:installed_apps/installed_apps.dart';
import 'package:installed_apps/app_info.dart';
import '../core/api/api_config.dart';
import '../features/app_scan/models/app_scan_result.dart';
import '../features/app_scan/models/scan_session.dart';

class AppScanService {
  Future<List<AppInfo>> _getInstalledApps() async {
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      try {
        List<AppInfo> apps = await InstalledApps.getInstalledApps(excludeSystemApps: false, withIcon: true);
        return apps;
      } catch (e) {
        debugPrint("Error fetching apps: $e");
        return [];
      }
    }
    return [];
  }

  Future<List<AppScanResult>> scanInstalledApps({Function(String msg)? onProgress}) async {
    List<AppScanResult> results = [];
    
    onProgress?.call("Fetching installed applications...");
    await Future.delayed(const Duration(milliseconds: 1000));
    
    List<AppInfo> realApps = await _getInstalledApps();
    List<Map<String, dynamic>> payloadApps = [];

    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) {
        throw Exception("Full System Application Scanning is strictly limited to native Android environments.");
    }

    if (realApps.isEmpty) {
        throw Exception("No third-party installed applications found organically on this device.");
    }

    for (var app in realApps) {
      payloadApps.add({
        "app_name": app.name,
        "package_name": app.packageName,
        "version_name": app.versionName,
        "is_system_app": false,
      });
    }

    String baseUrl = ApiConfig.baseUrl;
    
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.scanUrl}'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"apps": payloadApps}),
      ).timeout(const Duration(seconds: 120));

      if (response.statusCode == 200) {
        onProgress?.call("Running behavioral checks...");
        await Future.delayed(const Duration(milliseconds: 1500)); // ensure visual processing time
        
        final Map<String, dynamic> data = json.decode(response.body);
        final List<dynamic> riskyApps = data['risky_apps'] ?? [];
        
        for (var p in payloadApps) {
          bool isSafe = true;
          int riskScore = 100;
          String desc = "No threats found.";
          RiskLevel lvl = RiskLevel.low;
          
          for (var r in riskyApps) {
            if (r['package_name'] == p['package_name']) {
              isSafe = r['is_safe'] ?? false;
              riskScore = r['risk_score'] ?? 0;
              desc = (r['flags'] as List).join("\n");
              
              String rawLevel = r['risk_level'] ?? "High";
              if (rawLevel == "High") {
                lvl = RiskLevel.high;
              } else if (rawLevel == "Medium") {
                lvl = RiskLevel.medium;
              } else {
                lvl = RiskLevel.low;
              }
              break;
            }
          }
          
          results.add(AppScanResult(
            appName: p['app_name'],
            packageName: p['package_name'],
            isSafe: isSafe,
            riskLevel: lvl,
            riskScore: riskScore,
            description: desc,
          ));
        }
      } else {
        throw Exception("Server responded with code ${response.statusCode}");
      }
    } catch (e) {
      debugPrint("Scan API Error: $e");
      onProgress?.call("Error: Failed to connect to backend scanner.");
      throw Exception("Backend scan failed: $e");
    }

    onProgress?.call("Finalizing security report...");
    await Future.delayed(const Duration(milliseconds: 500));
    
    return results;
  }

  Future<bool> whitelistApp(String packageName) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/api/v1/whitelist'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"package_name": packageName}),
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<List<AppScanResult>> scanApkFile(String filePath, String fileName, {Function(String msg)? onProgress}) async {
    onProgress?.call("Uploading physical APK binary to server for Deep Scan Reverse Engineering...");
    await Future.delayed(const Duration(milliseconds: 1000));

    try {
      var request = http.MultipartRequest('POST', Uri.parse('${ApiConfig.scanUrl}/apk'));
      request.files.add(await http.MultipartFile.fromPath('file', filePath, filename: fileName));
      
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        onProgress?.call("Analyzing manifest, permissions, and Binary YARA signatures...");
        await Future.delayed(const Duration(milliseconds: 1500));
        
        final Map<String, dynamic> parsedBody = json.decode(response.body);
        if (parsedBody['status'] == 'success') {
           final Map<String, dynamic> r = parsedBody['data'];
           return [
             AppScanResult(
               appName: r['app_name'] ?? fileName,
               packageName: r['package_name'] ?? "unknown.physical.apk",
               isSafe: r['is_safe'],
               riskLevel: r['is_safe'] ? RiskLevel.low : RiskLevel.high,
               riskScore: r['risk_score'],
               description: (r['critical_flags'] as List).isEmpty ? "File signature and behavior strictly verified as safe." : (r['critical_flags'] as List).join("\\n"),
             )
           ];
        } else {
           throw Exception(parsedBody['message']);
        }
      } else {
         throw Exception("Server rejected payload. Code: ${response.statusCode}");
      }
    } catch (e) {
      debugPrint("APK Deep Scan Error: $e");
      onProgress?.call("Error: Failed to connect to backend scanner.");
      throw Exception("Backend scan failed: $e");
    }
  }


  ScanSession generateSessionSummary(List<AppScanResult> results) {
    int total = results.length;
    int safeCount = results.where((r) => r.isSafe).length;
    int riskCount = total - safeCount;
    int score = total == 0 ? 100 : ((safeCount / total) * 100).round();
    
    return ScanSession(
      totalAppsScanned: total,
      safeAppsCount: safeCount,
      riskyAppsCount: riskCount,
      overallSecurityScore: score,
    );
  }
}
