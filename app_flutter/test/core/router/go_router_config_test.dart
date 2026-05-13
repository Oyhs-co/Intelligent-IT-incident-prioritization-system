import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/core/router/go_router_config.dart';

void main() {
  test('resolveRedirect sends unauthenticated users to login', () {
    final result = resolveRedirect(
      isLoggedIn: false,
      location: '/client/home',
      role: 'user',
    );

    expect(result, '/login');
  });

  test('resolveRedirect sends logged in users away from auth routes', () {
    final result = resolveRedirect(
      isLoggedIn: true,
      location: '/login',
      role: 'admin',
    );

    expect(result, '/admin/dashboard');
  });

  test('resolveRedirect blocks role mismatch', () {
    final result = resolveRedirect(
      isLoggedIn: true,
      location: '/admin/users',
      role: 'user',
    );

    expect(result, '/client/home');
  });

  test('resolveRedirect allows valid route for role', () {
    final result = resolveRedirect(
      isLoggedIn: true,
      location: '/client/home',
      role: 'user',
    );

    expect(result, isNull);
  });

  test('role helpers map to home routes', () {
    expect(getHomeRouteForRole('admin'), '/admin/dashboard');
    expect(getHomeRouteForRole('technician'), '/technician/dashboard');
    expect(getHomeRouteForRole('analyst'), '/analyst/dashboard');
    expect(getHomeRouteForRole('user'), '/client/home');
  });

  test('isRouteAllowedForRole enforces role paths', () {
    expect(isRouteAllowedForRole('/admin/users', 'admin'), isTrue);
    expect(isRouteAllowedForRole('/admin/users', 'user'), isFalse);
    expect(isRouteAllowedForRole('/client/home', 'user'), isTrue);
    expect(isRouteAllowedForRole('/analyst/metrics', 'analyst'), isTrue);
  });
}
