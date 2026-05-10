import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../../../core/utils/app_constants.dart';
import '../models/auth_user.dart';

enum AuthStatus { uninitialized, authenticated, unauthenticated, loading }

class AuthState {
  final AuthStatus status;
  final AuthUser? user;
  final String? error;

  const AuthState({required this.status, this.user, this.error});

  AuthState copyWith({AuthStatus? status, AuthUser? user, String? error}) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      error: error,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
}

class AuthNotifier extends Notifier<AuthState> {
  final ApiClient _api = ApiClient();

  @override
  AuthState build() {
    _init();
    return const AuthState(status: AuthStatus.uninitialized);
  }

  Future<void> _init() async {
    await _api.init();
    if (_api.isAuthenticated) {
      try {
        final userData = await _api.request('GET', ApiEndpoints.me, auth: true);
        state = AuthState(
          status: AuthStatus.authenticated,
          user: AuthUser.fromJson(userData as Map<String, dynamic>),
        );
      } catch (_) {
        state = const AuthState(status: AuthStatus.unauthenticated);
      }
    } else {
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading, error: null);
    try {
      final data = await _api.request(
        'POST',
        ApiEndpoints.login,
        body: {'email': email, 'password': password},
      ) as Map<String, dynamic>;

      await _api.setTokens(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      );

      final userData = await _api.request('GET', ApiEndpoints.me, auth: true);
      final user = AuthUser.fromJson(userData as Map<String, dynamic>);

      state = AuthState(status: AuthStatus.authenticated, user: user);
    } on ApiException catch (e) {
      state = AuthState(status: AuthStatus.unauthenticated, error: e.message);
    } catch (e) {
      state = AuthState(status: AuthStatus.unauthenticated, error: 'Error de conexión: $e');
    }
  }

  Future<void> register({
    required String email,
    required String username,
    required String password,
    String? firstName,
    String? lastName,
    String? department,
  }) async {
    state = state.copyWith(status: AuthStatus.loading, error: null);
    try {
      await _api.request(
        'POST',
        ApiEndpoints.register,
        body: {
          'email': email,
          'username': username,
          'password': password,
          if (firstName != null && firstName.isNotEmpty) 'first_name': firstName,
          if (lastName != null && lastName.isNotEmpty) 'last_name': lastName,
          if (department != null && department.isNotEmpty) 'department': department,
        },
      );

      await login(email, password);
    } on ApiException catch (e) {
      state = AuthState(status: AuthStatus.unauthenticated, error: e.message);
    } catch (e) {
      state = AuthState(status: AuthStatus.unauthenticated, error: 'Error de conexión: $e');
    }
  }

  Future<void> logout() async {
    await _api.clearTokens();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final authProvider = NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);
