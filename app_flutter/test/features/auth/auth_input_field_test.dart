import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/auth/presentation/widgets/auth_input_field.dart';
import '../../helpers/test_app.dart';

void main() {
  testWidgets('AuthInputField toggles obscure text', (
    WidgetTester tester,
  ) async {
    final controller = TextEditingController();
    addTearDown(controller.dispose);

    await tester.pumpWidget(
      buildTestApp(
        AuthInputField(
          label: 'Password',
          icon: Icons.lock_outline,
          isPassword: true,
          controller: controller,
        ),
      ),
    );

    final fieldFinder = find.byType(TextField);
    TextField field = tester.widget(fieldFinder);
    expect(field.obscureText, isTrue);

    await tester.tap(find.byIcon(Icons.visibility_outlined));
    await tester.pump();

    field = tester.widget(fieldFinder);
    expect(field.obscureText, isFalse);
  });
}
