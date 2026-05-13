import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/client_portal/presentation/pages/new_report.dart';
import '../../helpers/test_app.dart';

void main() {
  testWidgets('NewReportPage renders basic fields', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(buildTestApp(const NewReportPage()));

    await tester.pump();

    expect(find.textContaining('titulo corto'), findsOneWidget);
    expect(find.textContaining('descripcion'), findsWidgets);
    expect(find.byType(ChoiceChip), findsNWidgets(10));
    expect(find.textContaining('enviar'), findsOneWidget);
  });
}
