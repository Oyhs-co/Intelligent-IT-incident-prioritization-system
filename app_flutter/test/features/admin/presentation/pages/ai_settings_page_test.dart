import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/admin/presentation/pages/ai_settings_page.dart';
import '../../../../helpers/test_app.dart';

void main() {
  testWidgets('AISettingsPage renders controls', (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(const AISettingsPage()));

    await tester.pump();

    expect(find.textContaining('Ajustes del Modelo IA'), findsOneWidget);
    expect(find.textContaining('Guardar Configuración'), findsOneWidget);
  });
}
