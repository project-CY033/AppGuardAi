enum PdfCheckStatus { safe, warning, risk }

class PdfCheck {
  final String title;
  final String description;
  final PdfCheckStatus status;

  PdfCheck({
    required this.title,
    required this.description,
    required this.status,
  });
}

class PdfScanReport {
  final String fileName;
  final String? id;
  final String fileSize;
  final int scanScore;
  final DateTime scanTime;
  final List<PdfCheck> checks;

  PdfScanReport({
    required this.fileName,
    this.id,
    required this.fileSize,
    required this.scanScore,
    required this.scanTime,
    required this.checks,
  });
}
