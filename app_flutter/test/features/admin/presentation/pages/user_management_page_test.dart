import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/admin/presentation/pages/user_management_page.dart';
import 'package:app_flutter/features/admin/models/providers/admin_providers.dart';
import '../../../../helpers/test_app.dart';

class TestUserManagementNotifier extends UserManagementNotifier {
  TestUserManagementNotifier(this._state);
  final UserManagementState _state;

  @override
  UserManagementState build() => _state;
}

void main() {
  testWidgets('UserManagementPage renders user list', (
    WidgetTester tester,
  ) async {
    final user = AppUser(
      id: '1',
      email: 'user@example.com',
      username: 'user',
      role: 'user',
      firstName: 'User',
      lastName: 'Test',
      fullName: 'User Test',
      isActive: true,
      isVerified: true,
      createdAt: '2026-05-10T08:00:00Z',
    );

    await tester.pumpWidget(
      buildTestApp(
        const UserManagementPage(),
        overrides: [
          userManagementProvider.overrideWith(
            () =>
                TestUserManagementNotifier(UserManagementState(users: [user])),
          ),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('Gestión de Usuarios'), findsOneWidget);
    expect(find.textContaining('User Test'), findsOneWidget);
  });
}
