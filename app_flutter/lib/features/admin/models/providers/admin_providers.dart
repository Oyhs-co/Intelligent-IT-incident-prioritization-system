import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/utils/app_constants.dart';

final logger = Logger();

class AppUser {
  final String id;
  final String email;
  final String username;
  final String role;
  final String firstName;
  final String lastName;
  final String fullName;
  final String? department;
  final bool isActive;
  final bool isVerified;
  final String? lastLogin;
  final String createdAt;

  AppUser({
    required this.id,
    required this.email,
    required this.username,
    required this.role,
    required this.firstName,
    required this.lastName,
    required this.fullName,
    this.department,
    required this.isActive,
    required this.isVerified,
    this.lastLogin,
    required this.createdAt,
  });

  String get roleDisplay {
    switch (role) {
      case 'admin':
        return 'Administrador';
      case 'analyst':
        return 'Analista';
      case 'technician':
        return 'Técnico';
      default:
        return 'Cliente';
    }
  }

  String get shortName {
    if (firstName.isNotEmpty && lastName.isNotEmpty) {
      return '$firstName $lastName';
    }
    return fullName.isNotEmpty ? fullName : username;
  }

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as String,
      email: json['email'] as String,
      username: json['username'] as String,
      role: json['role'] as String,
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
      fullName: json['full_name'] as String? ?? '',
      department: json['department'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      isVerified: json['is_verified'] as bool? ?? false,
      lastLogin: json['last_login'] as String?,
      createdAt: json['created_at'] as String,
    );
  }

  AppUser copyWith({
    String? email,
    String? username,
    String? role,
    String? firstName,
    String? lastName,
    String? department,
    bool? isActive,
  }) {
    return AppUser(
      id: id,
      email: email ?? this.email,
      username: username ?? this.username,
      role: role ?? this.role,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      fullName: fullName,
      department: department ?? this.department,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified,
      lastLogin: lastLogin,
      createdAt: createdAt,
    );
  }
}

class UserManagementState {
  final List<AppUser> users;
  final bool isLoading;
  final String? error;

  const UserManagementState({
    this.users = const [],
    this.isLoading = false,
    this.error,
  });

  UserManagementState copyWith({
    List<AppUser>? users,
    bool? isLoading,
    String? error,
  }) {
    return UserManagementState(
      users: users ?? this.users,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class UserManagementNotifier extends Notifier<UserManagementState> {
  final ApiClient _api = ApiClient();

  @override
  UserManagementState build() {
    return const UserManagementState();
  }

  Future<void> fetchUsers() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final data = await _api.request('GET', ApiEndpoints.users, auth: true);
      final items = (data['items'] as List<dynamic>)
          .map((e) => AppUser.fromJson(e as Map<String, dynamic>))
          .toList();
      state = UserManagementState(users: items, isLoading: false);
    } catch (e) {
      logger.e('Failed to fetch users: $e');
      state = state.copyWith(isLoading: false, error: 'Error al cargar usuarios: $e');
    }
  }

  Future<bool> createUser({
    required String email,
    required String username,
    required String password,
    required String firstName,
    required String lastName,
    String? department,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final data = await _api.request('POST', ApiEndpoints.register, body: {
        'email': email,
        'username': username,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
        if (department != null && department.isNotEmpty) 'department': department,
      }, auth: true);
      final user = AppUser.fromJson(data as Map<String, dynamic>);
      state = UserManagementState(users: [user, ...state.users], isLoading: false);
      return true;
    } catch (e) {
      logger.e('Failed to create user: $e');
      state = state.copyWith(isLoading: false, error: 'Error al crear usuario: $e');
      return false;
    }
  }

  Future<bool> updateUser({
    required String id,
    String? email,
    String? firstName,
    String? lastName,
    String? department,
    String? role,
    bool? isActive,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final body = <String, dynamic>{};
      if (email != null) body['email'] = email;
      if (firstName != null) body['first_name'] = firstName;
      if (lastName != null) body['last_name'] = lastName;
      if (department != null) body['department'] = department;
      if (role != null) body['role'] = role;
      if (isActive != null) body['is_active'] = isActive;

      final data = await _api.request('PUT', ApiEndpoints.user(id), body: body, auth: true);
      final updated = AppUser.fromJson(data as Map<String, dynamic>);
      state = UserManagementState(
        users: state.users.map((u) => u.id == id ? updated : u).toList(),
        isLoading: false,
      );
      return true;
    } catch (e) {
      logger.e('Failed to update user: $e');
      state = state.copyWith(isLoading: false, error: 'Error al actualizar usuario: $e');
      return false;
    }
  }

  Future<bool> deleteUser(String id) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _api.request('DELETE', ApiEndpoints.user(id), auth: true);
      state = UserManagementState(
        users: state.users.where((u) => u.id != id).toList(),
        isLoading: false,
      );
      return true;
    } catch (e) {
      logger.e('Failed to delete user: $e');
      state = state.copyWith(isLoading: false, error: 'Error al eliminar usuario: $e');
      return false;
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final userManagementProvider = NotifierProvider<UserManagementNotifier, UserManagementState>(UserManagementNotifier.new);
