import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/presentation/pages/dashboard_page.dart';
import 'package:app_flutter/features/analyst_dashboard/models/providers/analyst_providers.dart';
import 'package:app_flutter/features/client_portal/models/incident.dart';
import 'package:app_flutter/features/client_portal/models/providers/client_portal_providers.dart';
import '../../../../helpers/test_app.dart';

class TestIncidentNotifier extends IncidentNotifier {
  TestIncidentNotifier(this._seed);
  final List<Incident> _seed;

  @override
  List<Incident> build() => _seed;

  @override
  Future<void> fetchIncidents({
    int skip = 0,
    int limit = 100,
    String? status,
    int? priority,
    String? category,
  }) async {}
}

class TestAnalystFilterNotifier extends AnalystFilterNotifier {
  TestAnalystFilterNotifier(this._value);
  final String _value;

  @override
  String build() => _value;
}

void main() {
  testWidgets('AnalystDashboardPage shows empty state', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      buildTestApp(
        const AnalystDashboardPage(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier(const [])),
          analystFilterProvider.overrideWith(
            () => TestAnalystFilterNotifier('Todas'),
          ),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('No hay incidentes'), findsOneWidget);
  });

  testWidgets('AnalystDashboardPage renders tickets', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-101',
      title: 'VPN caida',
      description: 'Sin acceso remoto',
      status: 'open',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
      priorityLabel: 'Alta',
    );

    await tester.pumpWidget(
      buildTestApp(
        const AnalystDashboardPage(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier([incident])),
          analystFilterProvider.overrideWith(
            () => TestAnalystFilterNotifier('Todas'),
          ),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('Triage de Incidentes'), findsOneWidget);
    expect(find.text('VPN caida'), findsOneWidget);
  });
}
