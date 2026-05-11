import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/models/providers/analyst_metadata_providers.dart';

void main() {
  test('IncidentCategory.fromJson parses value and label', () {
    final json = {'value': 'hardware', 'label': 'Hardware'};
    final category = IncidentCategory.fromJson(json);

    expect(category.value, 'hardware');
    expect(category.label, 'Hardware');
  });

  test('PriorityOption.fromJson parses value and label', () {
    final json = {'value': 3, 'label': 'Alta'};
    final option = PriorityOption.fromJson(json);

    expect(option.value, 3);
    expect(option.label, 'Alta');
  });

  test('MetadataState defaults are empty and not loading', () {
    const state = MetadataState();

    expect(state.categories, isEmpty);
    expect(state.priorities, isEmpty);
    expect(state.isLoading, isFalse);
  });
}
