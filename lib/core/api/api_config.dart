import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiConfig {
  // Use 127.0.0.1 for physical devices (with adb reverse) or iOS simulators.
  // Use 10.0.2.2 for Android emulators if adb reverse is NOT used.
  static const String _hostIp = '127.0.0.1'; 
  
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000';
    }
    
    if (Platform.isAndroid) {
      // If you are using the Android Emulator and NOT adb reverse, 
      // you might need to change _hostIp to '10.0.2.2'
      return 'http://$_hostIp:8000';
    } else if (Platform.isIOS) {
      // For iOS Simulator, localhost/127.0.0.1 points to the host machine
      return 'http://127.0.0.1:8000';
    }
    
    return 'http://127.0.0.1:8000';
  }

  static String get scanUrl => '$baseUrl/api/v1/scan';
  static String get boostUrl => '$baseUrl/api/v1/boost';
  static String get cleanUrl => '$baseUrl/api/v1/clean';
}
