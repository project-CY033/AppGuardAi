import 'dart:convert';
import 'package:http/http.dart' as http;
import '../features/pdf_scan/models/pdf_scan_report.dart';
import 'dart:typed_data';

class PdfScanService {
  Future<PdfScanReport> analyzePdf(String? filePath, String fileName, {String fileSize = "0 MB", Uint8List? fileBytes}) async {
    String baseUrl = 'http://127.0.0.1:8000';
    
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/v1/pdf'));
      
      if (fileBytes != null) {
        request.files.add(http.MultipartFile.fromBytes('file', fileBytes, filename: fileName));
      } else if (filePath != null && filePath.isNotEmpty) {
        request.files.add(await http.MultipartFile.fromPath('file', filePath, filename: fileName));
      } else {
        throw Exception("No file payload provided.");
      }
      
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final Map<String, dynamic> parsedBody = json.decode(response.body);
        if (parsedBody['status'] == 'success') {
          final Map<String, dynamic> r = parsedBody['data'];
          List<PdfCheck> parsedChecks = [];
          if (r['checks'] != null) {
            for (var c in r['checks']) {
              PdfCheckStatus s = PdfCheckStatus.safe;
              if (c['status'] == 'warning') s = PdfCheckStatus.warning;
              if (c['status'] == 'risk') s = PdfCheckStatus.risk;

              parsedChecks.add(PdfCheck(
                title: c['title'] ?? 'Unknown Check',
                description: c['description'] ?? 'No description provided.',
                status: s,
              ));
            }
          }

          return PdfScanReport(
            fileName: fileName,
            id: parsedBody['id'],
            fileSize: fileSize,
            scanScore: r['scan_score'] ?? 100,
            scanTime: DateTime.now(),
            checks: parsedChecks,
          );
        } else {
          throw Exception("API returned an error: ${parsedBody['message']}");
        }
      } else {
        throw Exception("Server rejected payload. Code: ${response.statusCode}");
      }
    } catch (e) {
      throw Exception("Backend scan failed: $e");
    }
  }

  Future<bool> deletePdf(String id) async {
    String baseUrl = 'http://127.0.0.1:8000';
    try {
      final response = await http.delete(Uri.parse('$baseUrl/api/v1/pdf/$id'));
      if (response.statusCode == 200) {
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
