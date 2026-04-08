import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'boost_service.dart';
import 'models/boost_models.dart';

import 'dart:io';
import 'package:installed_apps/installed_apps.dart';

enum BoostState { idle, analyzing, animating, result }

class BoostController extends ChangeNotifier {
  BoostState state = BoostState.idle;
  String currentMessage = "Ready to Boost";
  double progress = 0.0;
  
  BoostResponseData? resultData;
  final BoostService _service = BoostService();

  // Device stats for UI
  int totalRamMb = 0;
  int currentRamUsageMb = 0;
  int backgroundApps = 0;

  BoostController() {
    _loadRealDeviceStats();
  }

  Future<void> _loadRealDeviceStats() async {
    try {
      if (!kIsWeb && Platform.isAndroid) {
        // Fetch Real App count
        final apps = await InstalledApps.getInstalledApps(excludeSystemApps: true);
        backgroundApps = apps.isNotEmpty ? apps.length : 24;

        // Fetch Real RAM stats from /proc/meminfo
        final file = File('/proc/meminfo');
        if (file.existsSync()) {
          final lines = await file.readAsLines();
          int memTotalKb = 0;
          int memAvailableKb = 0;
          
          for (var line in lines) {
            if (line.startsWith('MemTotal:')) {
              final parts = line.split(RegExp(r'\s+'));
              if (parts.length > 1) memTotalKb = int.tryParse(parts[1]) ?? 0;
            } else if (line.startsWith('MemAvailable:')) {
              final parts = line.split(RegExp(r'\s+'));
              if (parts.length > 1) memAvailableKb = int.tryParse(parts[1]) ?? 0;
            }
          }
          
          if (memTotalKb > 0) {
            totalRamMb = memTotalKb ~/ 1024;
            if (memAvailableKb > 0) {
              currentRamUsageMb = (memTotalKb - memAvailableKb) ~/ 1024;
            } else {
              currentRamUsageMb = (memTotalKb ~/ 2) ~/ 1024; // safe fallback
            }
          }
        }
      }
    } catch (e) {
      debugPrint("Failed to load real stats: $e");
    }

    // Ultimate Fallbacks if parsing fails
    if (totalRamMb == 0) totalRamMb = 8192;
    if (currentRamUsageMb == 0) currentRamUsageMb = 6500;
    if (backgroundApps == 0) backgroundApps = 24;

    notifyListeners();
  }

  void startBoost(BuildContext context) async {
    if (state != BoostState.idle) return;
    
    state = BoostState.analyzing;
    currentMessage = "Analyzing background processes...";
    notifyListeners();

    try {
      // 1. Fire analytical request to Backend
      resultData = await _service.optimizeDevice(
        estimatedRamUsageMb: currentRamUsageMb,
        totalRamMb: totalRamMb,
        backgroundAppsCount: backgroundApps,
        storagePressurePercent: 75.0, // mock pressure
        cpuUsagePercent: 35.0, // mock CPU
      );
      
      // 2. Transition into Animation State
      state = BoostState.animating;
      currentMessage = "Clearing memory...";
      notifyListeners();

      // Trigger standard visual progression timer
      _runVisualProgressTimer();

    } catch (e) {
      debugPrint("Boost Error: $e");
      currentMessage = "Boost failed. Please try again.";
      state = BoostState.idle;
      notifyListeners();
    }
  }

  void _runVisualProgressTimer() {
    progress = 0.0;
    const duration = Duration(milliseconds: 50);
    const totalTimeMs = 4000;
    int elapsed = 0;

    Timer.periodic(duration, (timer) {
      elapsed += duration.inMilliseconds;
      progress = (elapsed / totalTimeMs) * 100;

      if (progress >= 30 && progress < 60) {
        currentMessage = "Optimizing CPU usage...";
      } else if (progress >= 60 && progress < 90) {
        currentMessage = "Boosting performance...";
      } else if (progress >= 90) {
        currentMessage = "Finalizing...";
      }

      if (elapsed >= totalTimeMs) {
        timer.cancel();
        progress = 100.0;
        state = BoostState.result;
        currentMessage = "Boost Complete 🚀";
      }
      notifyListeners();
    });
  }

  void reset() {
    state = BoostState.idle;
    progress = 0.0;
    currentMessage = "Ready to Boost";
    resultData = null;
    notifyListeners();
  }
}
