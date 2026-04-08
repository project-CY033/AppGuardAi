class CleanCategoryItem {
  final String id;
  final String category;
  final String description;
  final int sizeBytes;
  final bool isSafeToClean;
  bool isSelected;

  CleanCategoryItem({
    required this.id,
    required this.category,
    required this.description,
    required this.sizeBytes,
    required this.isSafeToClean,
    this.isSelected = true,
  });

  factory CleanCategoryItem.fromJson(Map<String, dynamic> json) {
    return CleanCategoryItem(
      id: json['id'] ?? '',
      category: json['category'] ?? '',
      description: json['description'] ?? '',
      sizeBytes: json['size_bytes'] ?? 0,
      isSafeToClean: json['is_safe_to_clean'] ?? false,
      isSelected: json['is_safe_to_clean'] ?? false,
    );
  }
}

class CleanResponseData {
  final int totalCleanableBytes;
  final List<CleanCategoryItem> categories;
  final int storageHealthScore;

  CleanResponseData({
    required this.totalCleanableBytes,
    required this.categories,
    required this.storageHealthScore,
  });

  factory CleanResponseData.fromJson(Map<String, dynamic> json) {
    var rawCategories = json['categories'] as List? ?? [];
    List<CleanCategoryItem> list = rawCategories.map((i) => CleanCategoryItem.fromJson(i)).toList();
    
    return CleanResponseData(
      totalCleanableBytes: json['total_cleanable_bytes'] ?? 0,
      categories: list,
      storageHealthScore: json['storage_health_score'] ?? 100,
    );
  }
}
