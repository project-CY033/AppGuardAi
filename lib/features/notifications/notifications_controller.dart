import 'package:flutter/material.dart';
import 'models/notification_model.dart';

class NotificationsController extends ChangeNotifier {
  final List<NotificationModel> _notifications = [];
  List<NotificationModel> get notifications => List.unmodifiable(_notifications);

  NotificationsController() {
    _populateMockData();
  }

  int get unreadCount => _notifications.where((n) => !n.isRead).length;

  void _populateMockData() {
    _notifications.addAll([
      NotificationModel(
        id: '1',
        title: 'Scan Completed',
        message: 'All apps are safe. Your device is fully protected.',
        type: NotificationType.security,
        timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
      ),
      NotificationModel(
        id: '2',
        title: 'Risk Detected',
        message: 'Suspicious app found: "Malware.Example". Please review immediately.',
        type: NotificationType.warning,
        timestamp: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      NotificationModel(
        id: '3',
        title: 'PDF Scan Completed',
        message: 'No threats detected in your recently scanned document.',
        type: NotificationType.pdf,
        timestamp: DateTime.now().subtract(const Duration(days: 1)),
      ),
      NotificationModel(
        id: '4',
        title: 'System Update',
        message: 'A new security database update is available.',
        type: NotificationType.system,
        timestamp: DateTime.now().subtract(const Duration(days: 2)),
      ),
    ]);
    notifyListeners();
  }

  void markAsRead(String id) {
    final index = _notifications.indexWhere((n) => n.id == id);
    if (index != -1 && !_notifications[index].isRead) {
      _notifications[index] = _notifications[index].copyWith(isRead: true);
      notifyListeners();
    }
  }

  void markAllAsRead() {
    for (int i = 0; i < _notifications.length; i++) {
      _notifications[i] = _notifications[i].copyWith(isRead: true);
    }
    notifyListeners();
  }

  void removeNotification(String id) {
    _notifications.removeWhere((n) => n.id == id);
    notifyListeners();
  }

  void clearAll() {
    _notifications.clear();
    notifyListeners();
  }
}
