import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/client_portal/presentation/pages/incident_details.dart';
import 'package:app_flutter/features/client_portal/models/incident.dart';
import '../../helpers/test_app.dart';

void main() {
  testWidgets('IncidentDetailsPage shows resolution card when resolved', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-300',
      title: 'Printer error',
      description: 'Paper jam',
      status: 'resolved',
      resolution: 'Replaced toner',
      finalPriority: 'p3_high',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
    );

    await tester.pumpWidget(
      buildTestApp(IncidentDetailsPage(incident: incident)),
    );

    await tester.pump();

    expect(find.text('Printer error'), findsOneWidget);
    expect(find.textContaining('Resoluci'), findsOneWidget);
    expect(find.textContaining('Replaced toner'), findsOneWidget);
  });
}
