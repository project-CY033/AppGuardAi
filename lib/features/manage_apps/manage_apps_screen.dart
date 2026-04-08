import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../app/routes.dart';
import 'manage_apps_controller.dart';

class ManageAppsScreen extends StatelessWidget {
  const ManageAppsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ManageAppsController(),
      child: const _ManageAppsView(),
    );
  }
}

class _ManageAppsView extends StatelessWidget {
  const _ManageAppsView();

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<ManageAppsController>();

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textDark),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          "Manage apps",
          style: TextStyle(
            color: AppColors.textDark,
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert, color: AppColors.textDark),
            onPressed: () {},
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchBar(context, controller),
          _buildQuickActions(),
          _buildSortingHeader(controller),
          Expanded(
            child: controller.isLoading
                ? const Center(child: CircularProgressIndicator())
                : _buildAppList(context, controller),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar(BuildContext context, ManageAppsController controller) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(30),
        ),
        child: TextField(
          onChanged: controller.searchApps,
          decoration: const InputDecoration(
            hintText: "Search apps",
            hintStyle: TextStyle(color: Colors.grey),
            prefixIcon: Icon(Icons.search, color: Colors.grey),
            border: InputBorder.none,
            contentPadding: EdgeInsets.symmetric(vertical: 15),
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _quickActionItem(Icons.security, "App lock", Colors.green),
          _quickActionItem(Icons.copy, "Dual apps", Colors.orange),
          _quickActionItem(Icons.settings_input_component, "Background\nautostart", Colors.teal),
        ],
      ),
    );
  }

  Widget _quickActionItem(IconData icon, String label, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 12, color: AppColors.textDark),
        ),
      ],
    );
  }

  Widget _buildSortingHeader(ManageAppsController controller) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Row(
        children: [
          Text(
            "Sorting by app name",
            style: TextStyle(color: Colors.blue[800], fontWeight: FontWeight.w500),
          ),
          Icon(Icons.unfold_more, size: 16, color: Colors.blue[800]),
        ],
      ),
    );
  }

  Widget _buildAppList(BuildContext context, ManageAppsController controller) {
    if (controller.apps.isEmpty) {
      return const Center(child: Text("No apps found"));
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      itemCount: controller.apps.length,
      itemBuilder: (context, index) {
        final appDetails = controller.apps[index];
        return _buildAppItem(context, appDetails);
      },
    );
  }

  Widget _buildAppItem(BuildContext context, MockAppDetails appDetails) {
    return InkWell(
      onTap: () => Navigator.pushNamed(
        context, 
        AppRoutes.appInfo, 
        arguments: appDetails
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Row(
          children: [
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
              ),
              child: appDetails.app.icon != null 
                  ? Image.memory(appDetails.app.icon!, fit: BoxFit.contain)
                  : const Icon(Icons.android, size: 30, color: Colors.grey),
            ),
            const SizedBox(width: 15),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    appDetails.app.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: AppColors.textDark,
                    ),
                  ),
                ],
              ),
            ),
            Text(
              appDetails.storageSize,
              style: const TextStyle(color: Colors.grey, fontSize: 14),
            ),
            const SizedBox(width: 5),
            const Icon(Icons.chevron_right, color: Colors.grey, size: 20),
          ],
        ),
      ),
    );
  }
}
