import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/admin/presentation/pages/admin_ticket_audit_page.dart';
import 'package:app_flutter/features/client_portal/models/incident.dart';
import '../../../../helpers/test_app.dart';

void main() {
  testWidgets('AdminTicketAuditPage renders header and sections', (
    WidgetTester tester,
  ) async {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-777',
      title: 'Falla de impresora',
      description: 'Atasco de papel',
      status: 'open',
      createdAt: '2026-05-10T08:00:00Z',
      updatedAt: '2026-05-10T08:00:00Z',
    );

    await tester.pumpWidget(
      buildTestApp(AdminTicketAuditPage(ticket: incident)),
    );

    await tester.pumpAndSettle();

    expect(find.textContaining('Auditoría: T-777'), findsOneWidget);
    expect(find.textContaining('DATOS DEL REPORTE'), findsOneWidget);
    expect(find.textContaining('Sin registros de actividad'), findsOneWidget);
  });
}
