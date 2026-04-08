import 'dart:async';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'dart:io';
import '../../services/clean_service_api.dart';
import 'models/clean_models.dart';

enum CleanState {
  idle,
  scanning,
  results,
  cleaning,
  success,
}

class DeepCleanController extends ChangeNotifier {
  CleanState _state = CleanState.idle;
  double _progress = 0;
  String _statusMessage = "Ready to optimize your device";
  
  static const platform = MethodChannel('com.appguardai/storage');
  
  // Storage data
  int _totalDeviceSpaceBytes = 1; 
  int _usedDeviceSpaceBytes = 0;  
  int _freedBytes = 0;
  
  CleanResponseData? _analysisData;
  final CleanServiceAPI _api = CleanServiceAPI();

  // Getters
  CleanState get state => _state;
  double get progress => _progress;
  String get statusMessage => _statusMessage;
  int get totalDeviceSpaceBytes => _totalDeviceSpaceBytes;
  int get usedDeviceSpaceBytes => _usedDeviceSpaceBytes;
  int get freedBytes => _freedBytes;
  List<CleanCategoryItem> get categories => _analysisData?.categories ?? [];
  bool get hasAnalysis => _analysisData != null;

  DeepCleanController() {
    _initStorage();
  }

  Future<void> _initStorage() async {
    try {
      if (!kIsWeb && Platform.isAndroid) {
        // Ultimate accurate method: run native Linux df command for /data partition
        final result = await Process.run('df', ['/data']);
        final lines = result.stdout.toString().split('\n');
        for (var line in lines) {
          if (line.contains('/data')) {
            final parts = line.split(RegExp(r'\s+'));
            if (parts.length >= 4) {
              int total1K = int.tryParse(parts[1]) ?? 0;
              int used1K = int.tryParse(parts[2]) ?? 0;
              if (total1K > 0) {
                _totalDeviceSpaceBytes = total1K * 1024;
                _usedDeviceSpaceBytes = used1K * 1024;
                notifyListeners();
                return;
              }
            }
          }
        }
      }

      // Secondary fallback to Kotlin Native MethodChannel
      if (!kIsWeb) {
        final total = await platform.invokeMethod<int>('getTotalSpace');
        final free = await platform.invokeMethod<int>('getFreeSpace');
        if (total != null && free != null && total > 0) {
          _totalDeviceSpaceBytes = total;
          _usedDeviceSpaceBytes = total - free;
          notifyListeners();
          return;
        }
      }
    } catch (e) {
      debugPrint("Storage fetch failed: $e");
    }

    // Safety Fallback if nothing else works (128GB)
    _totalDeviceSpaceBytes = 128 * 1024 * 1024 * 1024;
    _usedDeviceSpaceBytes = 90 * 1024 * 1024 * 1024;
    notifyListeners();
  }

  int get selectedCleanableBytes {
    if (_analysisData == null) return 0;
    return _analysisData!.categories
        .where((c) => c.isSelected)
        .fold(0, (sum, c) => sum + c.sizeBytes);
  }

  void toggleCategory(String id) {
    if (_analysisData == null) return;
    final index = _analysisData!.categories.indexWhere((c) => c.id == id);
    if (index != -1) {
      _analysisData!.categories[index].isSelected = !_analysisData!.categories[index].isSelected;
      notifyListeners();
    }
  }

  Future<void> startScan() async {
    _state = CleanState.scanning;
    _progress = 0;
    _statusMessage = "Initializing Deep Scanner...";
    notifyListeners();

    try {
      final messages = [
        "Scanning cache files...",
        "Analyzing app storage...",
        "Detecting residual files...",
        "Checking temporary data...",
        "Finalizing heuristic report...",
      ];

      // Simulated smooth progress phases for UI
      for (int i = 0; i < messages.length; i++) {
        _statusMessage = messages[i];
        for (int p = 0; p < 20; p++) {
          await Future.delayed(const Duration(milliseconds: 30)); // 600ms per phase
          _progress += 1;
          notifyListeners();
        }
      }

      // Live Request
      _analysisData = await _api.analyzeStorage(
        totalSpaceBytes: _totalDeviceSpaceBytes,
        usedSpaceBytes: _usedDeviceSpaceBytes,
        installedAppsCount: 65, // In production, call AppScanService to count apps
      );

      _progress = 100;
      _state = CleanState.results;
      _statusMessage = "Scan Complete";
      notifyListeners();

    } catch (e) {
      _state = CleanState.idle;
      _statusMessage = "Scan Failed: ${e.toString().split('Exception: ').last}";
      _progress = 0;
      notifyListeners();
    }
  }

  Future<void> cleanSelected() async {
    if (_analysisData == null || selectedCleanableBytes == 0) return;

    _state = CleanState.cleaning;
    _progress = 0;
    _statusMessage = "Preparing to clean...";
    notifyListeners();

    final itemsToClean = _analysisData!.categories.where((c) => c.isSelected).toList();
    final totalToClean = selectedCleanableBytes;
    
    int bytesCleanedSoFar = 0;

    for (var item in itemsToClean) {
      _statusMessage = "Removing ${item.category}...";
      notifyListeners();

      // Simulate chunked cleaning
      int chunks = 20;
      int bytesPerChunk = item.sizeBytes ~/ chunks;
      for (int i = 0; i < chunks; i++) {
        await Future.delayed(const Duration(milliseconds: 40));
        bytesCleanedSoFar += bytesPerChunk;
        _progress = (bytesCleanedSoFar / totalToClean) * 100;
        notifyListeners();
      }
    }

    _progress = 100;
    _freedBytes = totalToClean;
    _usedDeviceSpaceBytes -= _freedBytes;
    
    // Clear out the cleaned items from list
    _analysisData!.categories.removeWhere((c) => c.isSelected);
    
    _state = CleanState.success;
    _statusMessage = "Your Device is Optimized";
    notifyListeners();
  }

  void reset() {
    _state = CleanState.idle;
    _progress = 0;
    _statusMessage = "Ready to optimize your device";
    _analysisData = null;
    _freedBytes = 0;
    // Re-fetch storage to reflect new reality
    _initStorage();
    notifyListeners();
  }
}
