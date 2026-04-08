import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:android_intent_plus/android_intent.dart';
import '../../services/scan_service.dart';
import 'models/app_scan_result.dart';
import 'models/scan_session.dart';

enum AppScanState { idle, loadingApps, scanning, completed, error }

class AppScanController extends ChangeNotifier {
  final AppScanService _service = AppScanService();
  
  AppScanState _state = AppScanState.idle;
  AppScanState get state => _state;

  double _progress = 0.0;
  double get progress => _progress;

  String _statusMessage = "Ready to scan.";
  String get statusMessage => _statusMessage;

  ScanSession? _currentSession;
  ScanSession? get currentSession => _currentSession;

  List<AppScanResult> _scanResults = [];
  List<AppScanResult> get scanResults => List.unmodifiable(_scanResults);
  
  final Set<String> _selectedRiskyApps = {};
  Set<String> get selectedRiskyApps => Set.unmodifiable(_selectedRiskyApps);

  PlatformFile? _selectedApk;
  PlatformFile? get selectedApk => _selectedApk;

  void toggleSelection(String packageName) {
    if (_selectedRiskyApps.contains(packageName)) {
      _selectedRiskyApps.remove(packageName);
    } else {
      _selectedRiskyApps.add(packageName);
    }
    notifyListeners();
  }

  void reset() {
    _state = AppScanState.idle;
    _progress = 0.0;
    _statusMessage = "Ready to scan.";
    _currentSession = null;
    _scanResults.clear();
    _selectedRiskyApps.clear();
    _selectedApk = null;
    notifyListeners();
  }

  Future<void> startDeviceScan() async {
    _state = AppScanState.scanning;
    _progress = 0.0;
    _statusMessage = "Starting device scan...";
    _scanResults.clear();
    _selectedRiskyApps.clear();
    _currentSession = null;
    notifyListeners();

    _simulateProgress(totalSeconds: 5); // Smooth progress simulation

    try {
      _scanResults = await _service.scanInstalledApps(
        onProgress: (msg) {
          _statusMessage = msg;
          notifyListeners();
        },
      );
      
      _currentSession = _service.generateSessionSummary(_scanResults);
      _progress = 100.0;
      _state = AppScanState.completed;
      _statusMessage = "Scan completed successfully.";
    } catch (e) {
      _state = AppScanState.error;
      _statusMessage = "Failed to complete scan: $e";
    }
    
    notifyListeners();
  }

  Future<void> pickAndScanApk() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['apk'],
      );

      if (result != null) {
        _selectedApk = result.files.first;
        if (_selectedApk!.path != null) {
          _startApkScan(_selectedApk!.path!, _selectedApk!.name);
        } else {
          _state = AppScanState.error;
          _statusMessage = "Cannot retrieve exact file path on this device.";
          notifyListeners();
        }
      }
    } catch (e) {
      _state = AppScanState.error;
      _statusMessage = "Error picking file: \$e";
      notifyListeners();
    }
  }

  Future<void> _startApkScan(String filePath, String fileName) async {
    _state = AppScanState.scanning;
    _progress = 0.0;
    _statusMessage = "Preparing APK analysis...";
    _scanResults.clear();
    _selectedRiskyApps.clear();
    _currentSession = null;
    notifyListeners();

    _simulateProgress(totalSeconds: 5);

    try {
      _scanResults = await _service.scanApkFile(
        filePath,
        fileName,
        onProgress: (msg) {
          _statusMessage = msg;
          notifyListeners();
        },
      );
      
      _currentSession = _service.generateSessionSummary(_scanResults);
      _progress = 100.0;
      _state = AppScanState.completed;
      _statusMessage = "APK analysis complete.";
    } catch (e) {
      _state = AppScanState.error;
      _statusMessage = "Failed to scan APK: $e";
    }
    
    notifyListeners();
  }

  void _simulateProgress({required int totalSeconds}) {
    int milliseconds = totalSeconds * 1000;
    int step = 50; // Update every 50ms
    double increment = 100.0 / (milliseconds / step);
    
    Future.doWhile(() async {
      await Future.delayed(Duration(milliseconds: step));
      if (_state != AppScanState.scanning) return false;
      
      if (_progress < 95.0) {
        _progress += increment;
        notifyListeners();
      }
      return true;
    });
  }

  // --- ACTIONS ---
  
  Future<void> uninstallApp(String packageName) async {
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      try {
        final AndroidIntent intent = AndroidIntent(
          action: 'android.settings.APPLICATION_DETAILS_SETTINGS',
          data: 'package:$packageName',
        );
        await intent.launch();
        
        // Remove from list proactively assuming the user uninstalls it
        _scanResults.removeWhere((app) => app.packageName == packageName);
        _currentSession = _service.generateSessionSummary(_scanResults);
        notifyListeners();
      } catch (e) {
        debugPrint("Error launching uninstall intent: $e");
      }
    } else {
        // Fallback for non-android simulation environments
        _scanResults.removeWhere((app) => app.packageName == packageName);
        _currentSession = _service.generateSessionSummary(_scanResults);
        notifyListeners();
    }
  }

  Future<void> ignoreApp(String packageName) async {
    final index = _scanResults.indexWhere((app) => app.packageName == packageName);
    if (index != -1) {
      final oldApp = _scanResults[index];
      
      // Hit backend API to securely log intent
      bool success = await _service.whitelistApp(packageName);
      
      if (success) {
          // Create a copied safe version instantly reflecting safely
          _scanResults[index] = AppScanResult(
            appName: oldApp.appName,
            packageName: oldApp.packageName,
            isSafe: true,
            riskLevel: RiskLevel.low,
            riskScore: 100,
            description: "User marked as safe.",
            iconPath: oldApp.iconPath,
          );
          _currentSession = _service.generateSessionSummary(_scanResults);
          notifyListeners();
      } else {
          _statusMessage = "Failed to whitelist app on server.";
          notifyListeners();
      }
    }
  }

  Future<void> uninstallSelected() async {
    for (String pkg in _selectedRiskyApps.toList()) {
      await uninstallApp(pkg);
    }
  }

  Future<void> ignoreSelected() async {
    for (String pkg in _selectedRiskyApps.toList()) {
      await ignoreApp(pkg);
    }
    _selectedRiskyApps.clear();
    notifyListeners();
  }
}
