import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/technician_dashboard/presentation/pages/technician_resolve_page.dart';
import 'package:app_flutter/features/client_portal/models/incident.dart';
import '../../../../helpers/test_app.dart';

void main() {
  testWidgets('TechnicianResolvePage requires resolution text', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-505',
      title: 'PC sin audio',
      description: 'No suena',
      status: 'in_progress',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
    );

    await tester.pumpWidget(
      buildTestApp(TechnicianResolvePage(ticket: incident)),
    );

    await tester.tap(find.textContaining('Marcar como Resuelto'));
    await tester.pump();

    expect(find.textContaining('Debes ingresar un reporte'), findsOneWidget);
  });
}
