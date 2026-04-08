import 'dart:async';
import 'package:flutter/material.dart';
import '../../services/scan_service.dart';
import '../app_scan/models/app_scan_result.dart';

enum ScanState {
  idle,
  scanning,
  safe,
  risk,
}

class DashboardController extends ChangeNotifier {
  ScanState _state = ScanState.idle;
  double _score = 100;
  String _status = "Scan Now to protect your device";
  double _progress = 0;
  List<AppScanResult> _lastResults = [];

  ScanState get state => _state;
  double get score => _score;
  String get status => _status;
  double get progress => _progress;
  List<AppScanResult> get lastResults => _lastResults;

  final AppScanService _scanService = AppScanService();

  Future<void> performScan(BuildContext context, {VoidCallback? onComplete}) async {
    if (_state == ScanState.scanning) return;

    _state = ScanState.scanning;
    _progress = 0;
    _status = "Initializing Security Engine...";
    _lastResults = [];
    notifyListeners();

    try {
      // Simulate connecting progress
      for (int i = 0; i <= 20; i += 5) {
        await Future.delayed(const Duration(milliseconds: 50));
        _progress = i.toDouble();
        notifyListeners();
      }

      // Live Backend Scanner Hook
      _lastResults = await _scanService.scanInstalledApps(
        onProgress: (msg) {
          _status = msg;
          if (_progress < 90) _progress += 10;
          notifyListeners();
        }
      );

      _progress = 100;
      
      // Calculate final deterministic score from session summary
      final summary = _scanService.generateSessionSummary(_lastResults);
      _score = summary.overallSecurityScore.toDouble();

      if (_score >= 80) {
        _state = ScanState.safe;
        _status = _score >= 95 ? "Safe – Everything looks good" : "System Secure - Minor risks noted";
      } else {
        _state = ScanState.risk;
        _status = "Critical Device Health – Immediate Action Recommended";
      }
      notifyListeners();
      
      if (onComplete != null) {
        await Future.delayed(const Duration(milliseconds: 800)); // Lets animation finish
        onComplete();
      }

    } catch (e) {
      _state = ScanState.risk;
      _status = "Scan Failed: ${e.toString().split('Exception: ').last}";
      _score = 0;
      _progress = 0;
      notifyListeners();
    }
  }
  
  void reset() {
    _state = ScanState.idle;
    _score = 100;
    _progress = 0;
    _status = "Scan Now to protect your device";
    _lastResults = [];
    notifyListeners();
  }
}
