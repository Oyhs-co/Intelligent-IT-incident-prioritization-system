import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/admin/presentation/pages/global_tickets_page.dart';
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
  testWidgets('GlobalTicketsPage renders tickets and KPIs', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-901',
      title: 'Servidor lento',
      description: 'Alto uso de CPU',
      status: 'open',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
      priorityLabel: 'Alta',
    );

    await tester.pumpWidget(
      buildTestApp(
        const GlobalTicketsPage(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier([incident])),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('Centro de Monitoreo Global'), findsOneWidget);
    expect(find.textContaining('REGISTRO GENERAL DE TICKETS'), findsOneWidget);
    expect(find.textContaining('Servidor lento'), findsOneWidget);
  });
}
