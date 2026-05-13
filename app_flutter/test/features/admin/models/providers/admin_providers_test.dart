import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/admin/models/providers/admin_providers.dart';

void main() {
  test('AppUser.fromJson and helpers work', () {
    final json = {
      'id': '1',
      'email': 'admin@example.com',
      'username': 'admin',
      'role': 'admin',
      'first_name': 'Ana',
      'last_name': 'Admin',
      'full_name': 'Ana Admin',
      'department': 'IT',
      'is_active': true,
      'is_verified': true,
      'last_login': null,
      'created_at': '2026-05-10T08:00:00Z',
    };

    final user = AppUser.fromJson(json);

    expect(user.roleDisplay, 'Administrador');
    expect(user.shortName, 'Ana Admin');
    expect(user.department, 'IT');
  });

  test('AppUser.copyWith updates fields', () {
    final user = AppUser(
      id: '2',
      email: 'u@example.com',
      username: 'user',
      role: 'user',
      firstName: 'User',
      lastName: 'One',
      fullName: 'User One',
      isActive: true,
      isVerified: false,
      createdAt: '2026-05-10T08:00:00Z',
    );

    final updated = user.copyWith(role: 'analyst', isActive: false);

    expect(updated.role, 'analyst');
    expect(updated.isActive, isFalse);
    expect(updated.email, 'u@example.com');
  });
}
