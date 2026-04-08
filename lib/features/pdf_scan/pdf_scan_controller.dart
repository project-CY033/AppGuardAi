import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../services/pdf_service.dart';
import 'models/pdf_scan_report.dart';

enum PdfScanState { idle, uploading, scanning, completed, error }

class PdfScanController extends ChangeNotifier {
  final PdfScanService _service = PdfScanService();

  PdfScanState _state = PdfScanState.idle;
  PdfScanState get state => _state;

  PlatformFile? _selectedFile;
  PlatformFile? get selectedFile => _selectedFile;

  PdfScanReport? _lastReport;
  PdfScanReport? get lastReport => _lastReport;

  double _progress = 0;
  double get progress => _progress;

  String _statusMessage = "Ready to scan";
  String get statusMessage => _statusMessage;

  Future<void> pickFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
        withData: true,
      );

      if (result != null) {
        _selectedFile = result.files.first;
        _state = PdfScanState.uploading;
        _lastReport = null;
        _progress = 0;
        notifyListeners();
        
        // Simulating upload
        await Future.delayed(const Duration(seconds: 1));
        _state = PdfScanState.idle; // Ready to start analysis
        notifyListeners();
      }
    } catch (e) {
      _state = PdfScanState.error;
      _statusMessage = "Error picking file: $e";
      notifyListeners();
    }
  }

  Future<void> startScan() async {
    if (_selectedFile == null) return;

    _state = PdfScanState.scanning;
    _progress = 0;
    _statusMessage = "Analyzing document structure...";
    notifyListeners();

    // Progress simulation
    _simulateProgress();

    try {
      final report = await _service.analyzePdf(
        _selectedFile!.path,
        _selectedFile!.name,
        fileSize: _formatBytes(_selectedFile!.size),
        fileBytes: _selectedFile!.bytes,
      );
      
      _lastReport = report;
      _state = PdfScanState.completed;
      _progress = 100;
      _statusMessage = "Scan complete";
      notifyListeners();
    } catch (e) {
      _state = PdfScanState.error;
      _statusMessage = "Scan failed: $e";
      notifyListeners();
    }
  }

  void _simulateProgress() async {
    const phases = [
      "Analyzing document structure...",
      "Scanning embedded scripts...",
      "Checking for malicious links...",
      "Inspecting metadata...",
      "Deep analysis in progress..."
    ];

    int phaseIndex = 0;
    while (_state == PdfScanState.scanning && _progress < 95) {
      await Future.delayed(const Duration(milliseconds: 100));
      _progress += 2;
      
      // Update status message periodically
      if (_progress.toInt() % 20 == 0 && phaseIndex < phases.length - 1) {
        phaseIndex++;
        _statusMessage = phases[phaseIndex];
      }
      notifyListeners();
    }
  }

  void reset() {
    _state = PdfScanState.idle;
    _selectedFile = null;
    _lastReport = null;
    _progress = 0;
    _statusMessage = "Ready to scan";
    notifyListeners();
  }

  void keepPdf() {
    _statusMessage = "Report saved successfully.";
    notifyListeners();
  }

  Future<void> deletePdf() async {
    if (_lastReport?.id != null) {
      _statusMessage = "Deleting file...";
      notifyListeners();
      bool success = await _service.deletePdf(_lastReport!.id!);
      if (success) {
        _statusMessage = "File successfully deleted from servers.";
        _lastReport = null;
        _selectedFile = null;
        _state = PdfScanState.idle;
      } else {
        _statusMessage = "Failed to delete file. It might be already removed.";
      }
      notifyListeners();
    }
  }

  String _formatBytes(int bytes) {
    if (bytes <= 0) return "0 B";
    const suffixes = ["B", "KB", "MB", "GB"];
    var i = (bytes.bitLength / 10).floor();
    var val = bytes / (1 << (i * 10));
    return "${val.toStringAsFixed(1)} ${suffixes[i]}";
  }
}
