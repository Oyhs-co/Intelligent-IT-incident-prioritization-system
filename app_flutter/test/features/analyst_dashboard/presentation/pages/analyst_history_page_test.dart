import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/presentation/pages/analyst_history_page.dart';
import 'package:app_flutter/features/client_portal/models/incident.dart';
import 'package:app_flutter/features/client_portal/models/providers/client_portal_providers.dart';
import '../../../../helpers/test_app.dart';

class TestIncidentNotifier extends IncidentNotifier {
  TestIncidentNotifier(this._seed);
  final List<Incident> _seed;

  @override
  List<Incident> build() => _seed;
}

void main() {
  testWidgets('AnalystHistoryPage shows empty state', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      buildTestApp(
        const AnalystHistoryPage(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier(const [])),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('No hay tickets resueltos'), findsOneWidget);
  });

  testWidgets('AnalystHistoryPage lists resolved tickets', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-301',
      title: 'Router reiniciado',
      description: 'Sin red',
      status: 'resolved',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
      explanation: 'Se reinicio el router',
      priorityLabel: 'Alta',
    );

    await tester.pumpWidget(
      buildTestApp(
        const AnalystHistoryPage(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier([incident])),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('Historial de Resueltos'), findsOneWidget);
    expect(find.textContaining('T-301'), findsOneWidget);
  });
}
