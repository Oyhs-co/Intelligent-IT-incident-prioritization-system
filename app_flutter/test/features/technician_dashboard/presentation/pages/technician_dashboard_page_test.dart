import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/technician_dashboard/presentation/pages/technician_dashboard_page.dart';
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

void main() {
  testWidgets('TechnicianDashboardPage shows empty state', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      buildTestApp(
        const TechnicianDashboardPage(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier(const [])),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('No tienes tickets pendientes'), findsOneWidget);
  });

  testWidgets('TechnicianDashboardPage lists in-progress tickets', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-404',
      title: 'Pantalla en negro',
      description: 'No inicia',
      status: 'in_progress',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
    );

    await tester.pumpWidget(
      buildTestApp(
        const TechnicianDashboardPage(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier([incident])),
        ],
      ),
    );

    await tester.pump();

    expect(find.text('Pantalla en negro'), findsOneWidget);
  });
}
