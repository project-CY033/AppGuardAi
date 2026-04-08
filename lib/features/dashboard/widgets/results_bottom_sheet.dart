import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../app_scan/models/app_scan_result.dart';
import '../../../core/theme/app_theme.dart';
import '../dashboard_controller.dart';

class ResultsBottomSheet extends StatelessWidget {
  final DashboardController controller;
  
  const ResultsBottomSheet({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    int safeCount = controller.lastResults.where((r) => r.isSafe).length;
    int riskCount = controller.lastResults.length - safeCount;
    int totalCount = controller.lastResults.length;

    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40,
              height: 5,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(10),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            "Security Report",
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: controller.score < 80 ? Colors.redAccent : AppColors.textDark,
            ),
          ),
          const SizedBox(height: 16),
          // Chart Row
          Row(
            children: [
              SizedBox(
                width: 120,
                height: 120,
                child: PieChart(
                  PieChartData(
                    sectionsSpace: 2,
                    centerSpaceRadius: 40,
                    sections: [
                      PieChartSectionData(
                        color: AppColors.primaryBlue,
                        value: safeCount.toDouble(),
                        title: '$safeCount',
                        radius: 12,
                        titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      if (riskCount > 0)
                        PieChartSectionData(
                          color: Colors.redAccent,
                          value: riskCount.toDouble(),
                          title: '$riskCount',
                          radius: 14,
                          titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildMetricRow("Score", "${controller.score.toInt()}%", controller.score >= 80 ? AppColors.primaryBlue : Colors.red),
                    const SizedBox(height: 8),
                    _buildMetricRow("Total Scanned", "$totalCount Apps", Colors.grey.shade700),
                    const SizedBox(height: 8),
                    _buildMetricRow("Threats", "$riskCount Found", riskCount > 0 ? Colors.redAccent : Colors.grey.shade700),
                  ],
                ),
              )
            ],
          ),
          const SizedBox(height: 24),
          const Text(
            "Flagged Applications",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textDark),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: riskCount == 0 
                ? const Center(child: Text("No threats detected.", style: TextStyle(color: Colors.grey)))
                : ListView.builder(
                    itemCount: controller.lastResults.length,
                    itemBuilder: (context, index) {
                      final app = controller.lastResults[index];
                      if (app.isSafe) return const SizedBox.shrink();
                      
                      return Card(
                        elevation: 1,
                        margin: const EdgeInsets.symmetric(vertical: 6),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        child: ExpansionTile(
                          leading: Icon(
                            Icons.warning_amber_rounded,
                            color: app.riskLevel == RiskLevel.high ? Colors.red : Colors.orange,
                          ),
                          title: Text(app.appName, style: const TextStyle(fontWeight: FontWeight.bold)),
                          subtitle: Text(app.packageName, style: const TextStyle(fontSize: 11)),
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Text(
                                app.description,
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade800),
                              ),
                            )
                          ],
                        ),
                      );
                    },
                  ),
          ),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primaryBlue,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () => Navigator.pop(context),
              child: const Text("Done", style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          )
        ],
      ),
    );
  }

  Widget _buildMetricRow(String label, String value, Color valueColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
        Text(value, style: TextStyle(color: valueColor, fontWeight: FontWeight.bold, fontSize: 14)),
      ],
    );
  }
}
