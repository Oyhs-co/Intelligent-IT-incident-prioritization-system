import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/presentation/pages/analyst_settings_page.dart';
import '../../../../helpers/test_app.dart';

void main() {
  testWidgets('AnalystSettingsPage renders profile settings', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(buildTestApp(const AnalystSettingsPage()));

    await tester.pump();

    expect(find.textContaining('Configuración de Perfil'), findsOneWidget);
    expect(find.textContaining('Estado Operativo'), findsOneWidget);
  });
}
