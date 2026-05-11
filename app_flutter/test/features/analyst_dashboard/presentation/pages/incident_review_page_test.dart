import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/presentation/pages/incident_review_page.dart';
import 'package:app_flutter/features/analyst_dashboard/models/providers/analyst_metadata_providers.dart';
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

class TestMetadataNotifier extends MetadataNotifier {
  TestMetadataNotifier(this._state);
  final MetadataState _state;

  @override
  MetadataState build() => _state;

  @override
  Future<void> fetchMetadata() async {}
}

void main() {
  testWidgets('IncidentReviewPage renders triage sections', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-201',
      title: 'Correo no sincroniza',
      description: 'Outlook no actualiza',
      status: 'new',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
    );

    final metadata = MetadataState(
      categories: [IncidentCategory(value: 'software', label: 'Software')],
      priorities: [PriorityOption(value: 3, label: 'Alta')],
      isLoading: false,
    );

    await tester.pumpWidget(
      buildTestApp(
        IncidentReviewPage(ticket: incident),
        overrides: [
          incidentProvider.overrideWith(() => TestIncidentNotifier([incident])),
          metadataProvider.overrideWith(() => TestMetadataNotifier(metadata)),
        ],
      ),
    );

    await tester.pump();
    await tester.pump();

    expect(find.textContaining('Revisión - T-201'), findsOneWidget);
    expect(find.textContaining('Decisión del Analista'), findsOneWidget);
    expect(find.textContaining('Guardar y Enviar'), findsOneWidget);
  });
}
