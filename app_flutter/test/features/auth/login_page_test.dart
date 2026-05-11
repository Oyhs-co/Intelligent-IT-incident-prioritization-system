import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/auth/presentation/pages/login_page.dart';
import 'package:app_flutter/features/auth/providers/auth_providers.dart';
import '../../helpers/test_app.dart';

class TestAuthNotifier extends AuthNotifier {
  TestAuthNotifier(this._state);
  final AuthState _state;

  @override
  AuthState build() => _state;

  @override
  Future<void> login(String email, String password) async {}

  @override
  Future<void> register({
    required String email,
    required String username,
    required String password,
    String? firstName,
    String? lastName,
    String? department,
  }) async {}

  @override
  Future<void> logout() async {}
}

void main() {
  testWidgets('LoginPage renders fields and button', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      buildTestApp(
        const LoginPage(),
        overrides: [
          authProvider.overrideWith(
            () => TestAuthNotifier(
              const AuthState(status: AuthStatus.unauthenticated),
            ),
          ),
        ],
      ),
    );

    expect(find.textContaining('Correo'), findsOneWidget);
    expect(find.textContaining('Contras'), findsOneWidget);
    expect(find.byType(FilledButton), findsOneWidget);
  });

  testWidgets('LoginPage shows snackbar on empty submit', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      buildTestApp(
        const LoginPage(),
        overrides: [
          authProvider.overrideWith(
            () => TestAuthNotifier(
              const AuthState(status: AuthStatus.unauthenticated),
            ),
          ),
        ],
      ),
    );

    await tester.tap(find.byType(FilledButton));
    await tester.pump();

    expect(find.textContaining('Email y contras'), findsOneWidget);
  });
}
