import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/providers/admin_providers.dart';

class UserManagementPage extends ConsumerStatefulWidget {
  const UserManagementPage({super.key});

  @override
  ConsumerState<UserManagementPage> createState() => _UserManagementPageState();
}

class _UserManagementPageState extends ConsumerState<UserManagementPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(userManagementProvider.notifier).fetchUsers();
    });
  }

  static const _roles = ['Cliente', 'Analista', 'Técnico', 'Administrador'];

  String _roleToBackend(String display) {
    switch (display) {
      case 'Administrador': return 'admin';
      case 'Analista': return 'analyst';
      case 'Técnico': return 'technician';
      default: return 'user';
    }
  }

  String _roleToDisplay(String backend) {
    switch (backend) {
      case 'admin': return 'Administrador';
      case 'analyst': return 'Analista';
      case 'technician': return 'Técnico';
      default: return 'Cliente';
    }
  }

  void _showAddUserDialog() {
    final nameCtrl = TextEditingController();
    final emailCtrl = TextEditingController();
    final usernameCtrl = TextEditingController();
    final passwordCtrl = TextEditingController();
    final departmentCtrl = TextEditingController();
    String selectedRole = 'Cliente';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: const Text('Añadir Usuario', style: TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'Nombre completo', hintText: 'Juan Pérez')),
                const SizedBox(height: 8),
                TextField(controller: emailCtrl, decoration: const InputDecoration(labelText: 'Correo electrónico', hintText: 'usuario@correo.com')),
                const SizedBox(height: 8),
                TextField(controller: usernameCtrl, decoration: const InputDecoration(labelText: 'Nombre de usuario', hintText: 'jperez')),
                const SizedBox(height: 8),
                TextField(controller: passwordCtrl, decoration: const InputDecoration(labelText: 'Contraseña'), obscureText: true),
                const SizedBox(height: 8),
                TextField(controller: departmentCtrl, decoration: const InputDecoration(labelText: 'Departamento (opcional)')),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  initialValue: selectedRole,
                  decoration: const InputDecoration(labelText: 'Rol'),
                  items: _roles.map((r) => DropdownMenuItem(value: r, child: Text(r))).toList(),
                  onChanged: (val) => setDialogState(() => selectedRole = val!),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                if (nameCtrl.text.isEmpty || emailCtrl.text.isEmpty || usernameCtrl.text.isEmpty || passwordCtrl.text.isEmpty) return;
                final parts = nameCtrl.text.trim().split(' ');
                final firstName = parts.isNotEmpty ? parts[0] : '';
                final lastName = parts.length > 1 ? parts.sublist(1).join(' ') : '';
                final notifier = ref.read(userManagementProvider.notifier);
                final success = await notifier.createUser(
                  email: emailCtrl.text.trim(),
                  username: usernameCtrl.text.trim(),
                  password: passwordCtrl.text,
                  firstName: firstName,
                  lastName: lastName,
                  department: departmentCtrl.text.trim().isEmpty ? null : departmentCtrl.text.trim(),
                );
                if (ctx.mounted) Navigator.pop(ctx);
                if (success) {
                  final backendRole = _roleToBackend(selectedRole);
                  final createdUsers = ref.read(userManagementProvider).users;
                  if (createdUsers.isNotEmpty) {
                    await notifier.updateUser(
                      id: createdUsers.first.id,
                      role: backendRole,
                    );
                  }
                  notifier.fetchUsers();
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Usuario creado exitosamente')));
                  }
                } else if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error al crear usuario'), backgroundColor: Colors.red));
                }
              },
              child: const Text('Guardar'),
            ),
          ],
        ),
      ),
    );
  }

  void _showEditUserDialog(AppUser user) {
    final firstNameCtrl = TextEditingController(text: user.firstName);
    final lastNameCtrl = TextEditingController(text: user.lastName);
    final emailCtrl = TextEditingController(text: user.email);
    final departmentCtrl = TextEditingController(text: user.department ?? '');
    String selectedRole = _roleToDisplay(user.role);
    bool isActive = user.isActive;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text('Editar Usuario: ${user.shortName}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: firstNameCtrl, decoration: const InputDecoration(labelText: 'Nombre')),
                const SizedBox(height: 8),
                TextField(controller: lastNameCtrl, decoration: const InputDecoration(labelText: 'Apellido')),
                const SizedBox(height: 8),
                TextField(controller: emailCtrl, decoration: const InputDecoration(labelText: 'Correo electrónico')),
                const SizedBox(height: 8),
                TextField(controller: departmentCtrl, decoration: const InputDecoration(labelText: 'Departamento')),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  initialValue: selectedRole,
                  decoration: const InputDecoration(labelText: 'Rol'),
                  items: _roles.map((r) => DropdownMenuItem(value: r, child: Text(r))).toList(),
                  onChanged: (val) => setDialogState(() => selectedRole = val!),
                ),
                const SizedBox(height: 8),
                SwitchListTile(
                  title: const Text('Activo'),
                  value: isActive,
                  onChanged: (val) => setDialogState(() => isActive = val),
                  contentPadding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                final success = await ref.read(userManagementProvider.notifier).updateUser(
                  id: user.id,
                  email: emailCtrl.text.trim(),
                  firstName: firstNameCtrl.text.trim(),
                  lastName: lastNameCtrl.text.trim(),
                  department: departmentCtrl.text.trim().isEmpty ? null : departmentCtrl.text.trim(),
                  role: _roleToBackend(selectedRole),
                  isActive: isActive,
                );
                if (ctx.mounted) Navigator.pop(ctx);
                if (success) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Usuario actualizado')));
                  }
                } else if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error al actualizar'), backgroundColor: Colors.red));
                }
              },
              child: const Text('Guardar Cambios'),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmDelete(AppUser user) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirmar Eliminación', style: TextStyle(fontWeight: FontWeight.bold)),
        content: Text('¿Estás seguro de eliminar a "${user.shortName}" (${user.email})? Esta acción no se puede deshacer.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final success = await ref.read(userManagementProvider.notifier).deleteUser(user.id);
              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Usuario ${user.shortName} eliminado')));
              } else if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error al eliminar'), backgroundColor: Colors.red));
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(userManagementProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        elevation: 0,
        title: const Text('Gestión de Usuarios', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(userManagementProvider.notifier).fetchUsers(),
          ),
          IconButton(
            icon: const Icon(Icons.person_add_alt_1),
            onPressed: _showAddUserDialog,
          ),
        ],
      ),
      body: _buildBody(state),
    );
  }

  Widget _buildBody(UserManagementState state) {
    if (state.isLoading && state.users.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.error != null && state.users.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text(state.error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.read(userManagementProvider.notifier).fetchUsers(),
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (state.users.isEmpty) {
      return const Center(child: Text('No hay usuarios registrados'));
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(userManagementProvider.notifier).fetchUsers(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: state.users.length,
        itemBuilder: (context, index) {
          final user = state.users[index];
          final roleColor = _roleColor(user.role);

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: user.isActive ? Colors.black.withValues(alpha: 0.08) : Colors.red.withValues(alpha: 0.2)),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: CircleAvatar(
                backgroundColor: roleColor.withValues(alpha: 0.1),
                child: Icon(Icons.person, color: roleColor),
              ),
              title: Text(user.shortName, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${user.email} • ${user.roleDisplay}'),
                  if (!user.isActive)
                    const Text('Inactivo', style: TextStyle(color: Colors.red, fontSize: 12, fontWeight: FontWeight.bold)),
                ],
              ),
              trailing: PopupMenuButton<String>(
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 'edit', child: Text('Editar Usuario')),
                  const PopupMenuItem(value: 'delete', child: Text('Eliminar Cuenta', style: TextStyle(color: Colors.red))),
                ],
                onSelected: (val) {
                  if (val == 'edit') {
                    _showEditUserDialog(user);
                  } else if (val == 'delete') {
                    _confirmDelete(user);
                  }
                },
              ),
            ),
          );
        },
      ),
    );
  }

  Color _roleColor(String role) {
    switch (role) {
      case 'admin': return const Color(0xFF7C3AED);
      case 'analyst': return const Color(0xFF2563EB);
      case 'technician': return const Color(0xFF059669);
      default: return const Color(0xFFD97706);
    }
  }
}
