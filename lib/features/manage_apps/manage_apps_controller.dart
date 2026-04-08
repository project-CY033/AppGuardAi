import 'package:flutter/foundation.dart';
import 'package:installed_apps/app_info.dart';
import 'package:installed_apps/installed_apps.dart';

class MockAppDetails {
  final AppInfo app;
  final String storageSize;

  MockAppDetails({required this.app, required this.storageSize});
}

class ManageAppsController extends ChangeNotifier {
  List<MockAppDetails> _allApps = [];
  List<MockAppDetails> _filteredApps = [];
  bool _isLoading = true;
  String _searchQuery = "";

  List<MockAppDetails> get apps => _filteredApps;
  bool get isLoading => _isLoading;
  String get searchQuery => _searchQuery;

  ManageAppsController() {
    _loadApps();
  }

  Future<void> _loadApps() async {
    _isLoading = true;
    notifyListeners();

    try {
      if (!kIsWeb) {
        List<AppInfo> installedApps = await InstalledApps.getInstalledApps(
          excludeSystemApps: true,
          withIcon: true,
        );
        
        _allApps = installedApps.map((app) {
          // Deterministic mock size based on app package name so it stays consistent
          int baseSize = app.packageName.length * 7;
          int offset = (app.name.length * 3.14).round() % 50;
          int finalSize = baseSize + offset > 10 ? baseSize + offset : 45;
          return MockAppDetails(
            app: app, 
            storageSize: "$finalSize MB",
          );
        }).toList();

        // Sort by name alphabetically
        _allApps.sort((a, b) => a.app.name.toLowerCase().compareTo(b.app.name.toLowerCase()));
        _filteredApps = List.from(_allApps);
      }
    } catch (e) {
      debugPrint("Failed to load apps: $e");
    }

    _isLoading = false;
    notifyListeners();
  }

  void searchApps(String query) {
    _searchQuery = query;
    if (query.isEmpty) {
      _filteredApps = List.from(_allApps);
    } else {
      _filteredApps = _allApps.where((mock) {
        return mock.app.name.toLowerCase().contains(query.toLowerCase());
      }).toList();
    }
    notifyListeners();
  }
}
