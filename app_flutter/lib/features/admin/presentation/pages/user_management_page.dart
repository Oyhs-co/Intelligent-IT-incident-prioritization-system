import 'package:flutter/material.dart';

class UserManagementPage extends StatelessWidget {
  const UserManagementPage({super.key});

  @override
  Widget build(BuildContext context) {
    final mockUsers = [
      {'name': 'Juan Pérez', 'email': 'cliente@test.com', 'role': 'Cliente'},
      {'name': 'Ana García', 'email': 'analista@test.com', 'role': 'Analista'},
      {'name': 'Roberto Silva', 'email': 'tecnico@test.com', 'role': 'Técnico'},
      {'name': 'Admin Root', 'email': 'admin@test.com', 'role': 'Administrador'},
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        elevation: 0,
        title: const Text('Gestión de Usuarios', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_add_alt_1),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Añadir usuario (Simulado)')));
            },
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: mockUsers.length,
        itemBuilder: (context, index) {
          final user = mockUsers[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: Colors.black.withValues(alpha: 0.08)),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: CircleAvatar(
                backgroundColor: const Color(0xFF2563EB).withValues(alpha: 0.1),
                child: const Icon(Icons.person, color: Color(0xFF2563EB)),
              ),
              title: Text(user['name']!, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('${user['email']} • Rol: ${user['role']}'),
              trailing: PopupMenuButton(
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 'edit', child: Text('Editar Rol')),
                  const PopupMenuItem(value: 'suspend', child: Text('Suspender Cuenta', style: TextStyle(color: Colors.red))),
                ],
                onSelected: (val) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Acción $val sobre ${user['name']} (Simulada)')));
                },
              ),
            ),
          );
        },
      ),
    );
  }
}
