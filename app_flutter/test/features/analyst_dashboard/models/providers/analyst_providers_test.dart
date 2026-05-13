import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:app_flutter/features/analyst_dashboard/models/providers/analyst_providers.dart';

void main() {
  test('AnalystFilterNotifier defaults and updates', () {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    expect(container.read(analystFilterProvider), 'Todas');

    container.read(analystFilterProvider.notifier).setFilter('Alta');
    expect(container.read(analystFilterProvider), 'Alta');
  });
}
