import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/client_portal/presentation/pages/client_home.dart';
import 'package:app_flutter/features/client_portal/models/incident.dart';
import 'package:app_flutter/features/client_portal/models/providers/client_portal_providers.dart';
import '../../helpers/test_app.dart';

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

class TestClientFilterNotifier extends ClientFilterNotifier {
  TestClientFilterNotifier(this._value);
  final String _value;

  @override
  String build() => _value;
}

void main() {
  testWidgets('ClientHome shows empty state', (WidgetTester tester) async {
    await tester.pumpWidget(
      buildTestApp(
        const ClientHome(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier(const [])),
          clientFilterProvider.overrideWith(
            () => TestClientFilterNotifier('Todos'),
          ),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('no tienes incidentes'), findsOneWidget);
  });

  testWidgets('ClientHome renders incident list', (WidgetTester tester) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-200',
      title: 'Printer error',
      description: 'Paper jam',
      status: 'resolved',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
    );

    await tester.pumpWidget(
      buildTestApp(
        const ClientHome(),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier([incident])),
          clientFilterProvider.overrideWith(
            () => TestClientFilterNotifier('Todos'),
          ),
        ],
      ),
    );

    await tester.pump();

    expect(find.text('Printer error'), findsOneWidget);
    expect(find.text('resuelto'), findsOneWidget);
  });
}
