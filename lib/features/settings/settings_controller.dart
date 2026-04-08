import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsController extends ChangeNotifier {
  late SharedPreferences _prefs;

  // Basic Settings
  bool _notificationsEnabled = true;
  bool _darkMode = false;
  bool _autoScanOnInstall = true;
  String _scanFrequency = 'Daily';

  // Advanced Settings
  bool _realTimeProtection = true;
  bool _backgroundScanning = true;
  bool _deepScanMode = false;
  bool _networkMonitoring = false;
  String _threatSensitivity = 'Medium';

  // Privacy Settings
  bool _shareAnonymizedData = false;
  bool _firstLaunchCompleted = false;

  // Getters
  bool get notificationsEnabled => _notificationsEnabled;
  bool get darkMode => _darkMode;
  bool get autoScanOnInstall => _autoScanOnInstall;
  String get scanFrequency => _scanFrequency;
  
  bool get realTimeProtection => _realTimeProtection;
  bool get backgroundScanning => _backgroundScanning;
  bool get deepScanMode => _deepScanMode;
  bool get networkMonitoring => _networkMonitoring;
  String get threatSensitivity => _threatSensitivity;
  
  bool get shareAnonymizedData => _shareAnonymizedData;
  bool get firstLaunchCompleted => _firstLaunchCompleted;

  SettingsController() {
    _initPrefs();
  }

  Future<void> _initPrefs() async {
    _prefs = await SharedPreferences.getInstance();
    _loadSettings();
  }

  void _loadSettings() {
    _notificationsEnabled = _prefs.getBool('notificationsEnabled') ?? true;
    _darkMode = _prefs.getBool('darkMode') ?? false;
    _autoScanOnInstall = _prefs.getBool('autoScanOnInstall') ?? true;
    _scanFrequency = _prefs.getString('scanFrequency') ?? 'Daily';

    _realTimeProtection = _prefs.getBool('realTimeProtection') ?? true;
    _backgroundScanning = _prefs.getBool('backgroundScanning') ?? true;
    _deepScanMode = _prefs.getBool('deepScanMode') ?? false;
    _networkMonitoring = _prefs.getBool('networkMonitoring') ?? false;
    _threatSensitivity = _prefs.getString('threatSensitivity') ?? 'Medium';

    _shareAnonymizedData = _prefs.getBool('shareAnonymizedData') ?? false;
    _firstLaunchCompleted = _prefs.getBool('firstLaunchCompleted') ?? false;
    
    notifyListeners();
  }

  // --- Actions ---

  void toggleNotifications(bool value) {
    _notificationsEnabled = value;
    _prefs.setBool('notificationsEnabled', value);
    notifyListeners();
  }

  void toggleDarkMode(bool value) {
    _darkMode = value;
    _prefs.setBool('darkMode', value);
    notifyListeners();
  }

  void toggleAutoScan(bool value) {
    _autoScanOnInstall = value;
    _prefs.setBool('autoScanOnInstall', value);
    notifyListeners();
  }

  void setScanFrequency(String value) {
    _scanFrequency = value;
    _prefs.setString('scanFrequency', value);
    notifyListeners();
  }

  void toggleRealTimeProtection(bool value) {
    _realTimeProtection = value;
    _prefs.setBool('realTimeProtection', value);
    notifyListeners();
  }

  void toggleBackgroundScanning(bool value) {
    _backgroundScanning = value;
    _prefs.setBool('backgroundScanning', value);
    notifyListeners();
  }

  void toggleDeepScanMode(bool value) {
    _deepScanMode = value;
    _prefs.setBool('deepScanMode', value);
    notifyListeners();
  }

  void toggleNetworkMonitoring(bool value) {
    _networkMonitoring = value;
    _prefs.setBool('networkMonitoring', value);
    notifyListeners();
  }

  void setThreatSensitivity(String value) {
    _threatSensitivity = value;
    _prefs.setString('threatSensitivity', value);
    notifyListeners();
  }

  void toggleAnonymizedData(bool value) {
    _shareAnonymizedData = value;
    _prefs.setBool('shareAnonymizedData', value);
    notifyListeners();
  }

  Future<void> clearScanHistory() async {
    // In a real app this would call ReportsController/AppScanService logic
    // or clear a local database of scan reports.
    debugPrint("Scan history cleared.");
  }

  Future<void> resetAllSettings() async {
    await _prefs.clear();
    _loadSettings(); // Reloads default values
  }

  void completeFirstLaunch() {
    _firstLaunchCompleted = true;
    _prefs.setBool('firstLaunchCompleted', true);
    notifyListeners();
  }
}
