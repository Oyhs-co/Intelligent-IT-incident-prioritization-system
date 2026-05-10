import 'package:flutter_riverpod/flutter_riverpod.dart';

class AppUser {
  final String id;
  final String name;
  final String email;
  final String role;

  AppUser({required this.id, required this.name, required this.email, required this.role});

  AppUser copyWith({String? name, String? email, String? role}) {
    return AppUser(
      id: id,
      name: name ?? this.name,
      email: email ?? this.email,
      role: role ?? this.role,
    );
  }
}

class UserManagementNotifier extends Notifier<List<AppUser>> {
  @override
  List<AppUser> build() => [
    AppUser(id: '1', name: 'Juan Pérez', email: 'cliente@test.com', role: 'Cliente'),
    AppUser(id: '2', name: 'Ana García', email: 'analista@test.com', role: 'Analista'),
    AppUser(id: '3', name: 'Roberto Silva', email: 'tecnico@test.com', role: 'Técnico'),
    AppUser(id: '4', name: 'Admin Root', email: 'admin@test.com', role: 'Administrador'),
  ];

  void addUser(String name, String email, String role) {
    state = [...state, AppUser(id: DateTime.now().millisecondsSinceEpoch.toString(), name: name, email: email, role: role)];
  }

  void updateRole(String id, String newRole) {
    state = state.map((u) => u.id == id ? u.copyWith(role: newRole) : u).toList();
  }

  void deleteUser(String id) {
    state = state.where((u) => u.id != id).toList();
  }
}

final userManagementProvider = NotifierProvider<UserManagementNotifier, List<AppUser>>(UserManagementNotifier.new);
