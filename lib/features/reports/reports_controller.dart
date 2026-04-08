import 'package:flutter/material.dart';
import 'models/scan_report.dart';

enum ReportFilterType { all, safe, risk }

class ReportsController extends ChangeNotifier {
  final List<ScanReport> _allReports = [
    ScanReport(
      id: '1',
      appName: 'WhatsApp',
      packageName: 'com.whatsapp',
      status: 'Safe',
      riskScore: 98,
      scanTime: DateTime.now().subtract(const Duration(minutes: 10)),
    ),
    ScanReport(
      id: '2',
      appName: 'Fake Banking App',
      packageName: 'com.malware.bank',
      status: 'Risk',
      riskScore: 12,
      scanTime: DateTime.now().subtract(const Duration(hours: 2)),
    ),
    ScanReport(
      id: '3',
      appName: 'Instagram',
      packageName: 'com.instagram.android',
      status: 'Safe',
      riskScore: 95,
      scanTime: DateTime.now().subtract(const Duration(days: 1)),
    ),
    ScanReport(
      id: '4',
      appName: 'Unknown File.apk',
      packageName: 'manual.upload.file',
      status: 'Risk',
      riskScore: 35,
      scanTime: DateTime.now().subtract(const Duration(days: 2)),
    ),
  ];

  ReportFilterType _currentFilter = ReportFilterType.all;
  ReportFilterType get currentFilter => _currentFilter;

  List<ScanReport> get reports {
    if (_currentFilter == ReportFilterType.safe) {
      return _allReports.where((r) => r.status == 'Safe').toList();
    } else if (_currentFilter == ReportFilterType.risk) {
      return _allReports.where((r) => r.status == 'Risk').toList();
    }
    return _allReports;
  }

  void setFilter(ReportFilterType filter) {
    _currentFilter = filter;
    notifyListeners();
  }

  // Summary Stats
  int get totalScans => _allReports.length;
  int get safeCount => _allReports.where((r) => r.status == 'Safe').length;
  int get riskCount => _allReports.where((r) => r.status == 'Risk').length;
  
  String get lastScanTime {
    if (_allReports.isEmpty) return "Never";
    // For demo, just returning the first one's time in a readable format
    return "Today 10:32 AM"; 
  }
}
