import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/auth/models/auth_user.dart';

void main() {
  test('fromJson parses user fields', () {
    final json = {
      'id': '1',
      'email': 'user@example.com',
      'username': 'user01',
      'role': 'admin',
      'first_name': 'Ana',
      'last_name': 'Diaz',
      'full_name': 'Ana Diaz',
      'department': 'IT',
      'is_active': true,
      'is_verified': false,
      'last_login': '2026-05-10T10:00:00Z',
      'created_at': '2026-05-01T08:00:00Z',
    };

    final user = AuthUser.fromJson(json);

    expect(user.id, '1');
    expect(user.email, 'user@example.com');
    expect(user.username, 'user01');
    expect(user.role, 'admin');
    expect(user.firstName, 'Ana');
    expect(user.lastName, 'Diaz');
    expect(user.fullName, 'Ana Diaz');
    expect(user.department, 'IT');
    expect(user.isActive, isTrue);
    expect(user.isVerified, isFalse);
    expect(user.lastLogin, '2026-05-10T10:00:00Z');
    expect(user.createdAt, '2026-05-01T08:00:00Z');
  });

  test('toJson returns expected map', () {
    final user = AuthUser(
      id: '2',
      email: 'test@example.com',
      username: 'test',
      role: 'user',
      firstName: 'Test',
      lastName: 'User',
      fullName: 'Test User',
      department: 'Ops',
      isActive: true,
      isVerified: true,
      lastLogin: null,
      createdAt: '2026-05-02T10:00:00Z',
    );

    final json = user.toJson();

    expect(json['id'], '2');
    expect(json['email'], 'test@example.com');
    expect(json['username'], 'test');
    expect(json['role'], 'user');
    expect(json['first_name'], 'Test');
    expect(json['last_name'], 'User');
    expect(json['full_name'], 'Test User');
    expect(json['department'], 'Ops');
    expect(json['is_active'], isTrue);
    expect(json['is_verified'], isTrue);
    expect(json['last_login'], isNull);
    expect(json['created_at'], '2026-05-02T10:00:00Z');
  });
}
