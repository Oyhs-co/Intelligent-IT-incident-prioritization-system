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


  Color _roleColor(String role) {
    switch (role) {
      case 'admin':       return const Color(0xFF7C3AED);
      case 'analyst':     return const Color(0xFF2563EB);
      case 'technician':  return const Color(0xFF059669);
      default:            return const Color(0xFFD97706);
    }
  }

  IconData _roleIcon(String role) {
    switch (role) {
      case 'admin':       return Icons.admin_panel_settings_outlined;
      case 'analyst':     return Icons.analytics_outlined;
      case 'technician':  return Icons.build_outlined;
      default:            return Icons.person_outline;
    }
  }

  InputDecoration _inputDecoration(BuildContext context, String label, {IconData? icon}) {
    final cs = Theme.of(context).colorScheme;
    return InputDecoration(
      labelText: label,
      prefixIcon: icon != null ? Icon(icon, size: 18, color: cs.onSurfaceVariant) : null,
      filled: true,
      fillColor: cs.surfaceContainerHighest.withValues(alpha: 0.45),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: cs.outlineVariant),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: cs.outlineVariant),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide(color: cs.primary, width: 1.5),
      ),
      labelStyle: TextStyle(color: cs.onSurfaceVariant, fontSize: 13),
    );
  }



  void _showAddUserDialog() {
    final nameCtrl       = TextEditingController();
    final emailCtrl      = TextEditingController();
    final usernameCtrl   = TextEditingController();
    final passwordCtrl   = TextEditingController();
    final departmentCtrl = TextEditingController();
    String selectedRole  = 'Cliente';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => _StyledDialog(
          title: 'Nuevo Usuario',
          icon: Icons.person_add_outlined,
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancelar'),
            ),
            FilledButton.icon(
              icon: const Icon(Icons.save_outlined, size: 16),
              label: const Text('Guardar'),
              onPressed: () async {
                if (nameCtrl.text.isEmpty || emailCtrl.text.isEmpty ||
                    usernameCtrl.text.isEmpty || passwordCtrl.text.isEmpty) return;
                final parts     = nameCtrl.text.trim().split(' ');
                final firstName = parts.isNotEmpty ? parts[0] : '';
                final lastName  = parts.length > 1 ? parts.sublist(1).join(' ') : '';
                final notifier  = ref.read(userManagementProvider.notifier);
                final success   = await notifier.createUser(
                  email:      emailCtrl.text.trim(),
                  username:   usernameCtrl.text.trim(),
                  password:   passwordCtrl.text,
                  firstName:  firstName,
                  lastName:   lastName,
                  department: departmentCtrl.text.trim().isEmpty ? null : departmentCtrl.text.trim(),
                );
                if (ctx.mounted) Navigator.pop(ctx);
                if (success) {
                  final backendRole   = _roleToBackend(selectedRole);
                  final createdUsers  = ref.read(userManagementProvider).users;
                  if (createdUsers.isNotEmpty) {
                    await notifier.updateUser(id: createdUsers.first.id, role: backendRole);
                  }
                  notifier.fetchUsers();
                  if (mounted) {
                    _showSnack('Usuario creado exitosamente', isError: false);
                  }
                } else if (mounted) {
                  _showSnack('Error al crear usuario', isError: true);
                }
              },
            ),
          ],
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: nameCtrl,       decoration: _inputDecoration(ctx, 'Nombre completo', icon: Icons.badge_outlined)),
              const SizedBox(height: 12),
              TextField(controller: emailCtrl,      decoration: _inputDecoration(ctx, 'Correo electrónico', icon: Icons.alternate_email)),
              const SizedBox(height: 12),
              TextField(controller: usernameCtrl,   decoration: _inputDecoration(ctx, 'Nombre de usuario', icon: Icons.account_circle_outlined)),
              const SizedBox(height: 12),
              TextField(controller: passwordCtrl,   decoration: _inputDecoration(ctx, 'Contraseña', icon: Icons.lock_outline), obscureText: true),
              const SizedBox(height: 12),
              TextField(controller: departmentCtrl, decoration: _inputDecoration(ctx, 'Departamento (opcional)', icon: Icons.corporate_fare_outlined)),
              const SizedBox(height: 12),
              _RoleDropdown(
                value: selectedRole,
                roles: _roles,
                decoration: _inputDecoration(ctx, 'Rol', icon: Icons.shield_outlined),
                onChanged: (val) => setDialogState(() => selectedRole = val!),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showEditUserDialog(AppUser user) {
    final firstNameCtrl  = TextEditingController(text: user.firstName);
    final lastNameCtrl   = TextEditingController(text: user.lastName);
    final emailCtrl      = TextEditingController(text: user.email);
    final departmentCtrl = TextEditingController(text: user.department ?? '');
    String selectedRole  = _roleToDisplay(user.role);
    bool   isActive      = user.isActive;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => _StyledDialog(
          title: 'Editar Usuario',
          icon: Icons.manage_accounts_outlined,
          subtitle: user.shortName,
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancelar'),
            ),
            FilledButton.icon(
              icon: const Icon(Icons.save_outlined, size: 16),
              label: const Text('Guardar Cambios'),
              onPressed: () async {
                final success = await ref.read(userManagementProvider.notifier).updateUser(
                  id:         user.id,
                  email:      emailCtrl.text.trim(),
                  firstName:  firstNameCtrl.text.trim(),
                  lastName:   lastNameCtrl.text.trim(),
                  department: departmentCtrl.text.trim().isEmpty ? null : departmentCtrl.text.trim(),
                  role:       _roleToBackend(selectedRole),
                  isActive:   isActive,
                );
                if (ctx.mounted) Navigator.pop(ctx);
                if (success) {
                  if (mounted) _showSnack('Usuario actualizado', isError: false);
                } else if (mounted) {
                  _showSnack('Error al actualizar', isError: true);
                }
              },
            ),
          ],
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Expanded(child: TextField(controller: firstNameCtrl, decoration: _inputDecoration(ctx, 'Nombre', icon: Icons.badge_outlined))),
                  const SizedBox(width: 10),
                  Expanded(child: TextField(controller: lastNameCtrl,  decoration: _inputDecoration(ctx, 'Apellido'))),
                ],
              ),
              const SizedBox(height: 12),
              TextField(controller: emailCtrl,      decoration: _inputDecoration(ctx, 'Correo electrónico', icon: Icons.alternate_email)),
              const SizedBox(height: 12),
              TextField(controller: departmentCtrl, decoration: _inputDecoration(ctx, 'Departamento', icon: Icons.corporate_fare_outlined)),
              const SizedBox(height: 12),
              _RoleDropdown(
                value: selectedRole,
                roles: _roles,
                decoration: _inputDecoration(ctx, 'Rol', icon: Icons.shield_outlined),
                onChanged: (val) => setDialogState(() => selectedRole = val!),
              ),
              const SizedBox(height: 4),
              _ActiveToggle(
                value: isActive,
                onChanged: (val) => setDialogState(() => isActive = val),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _confirmDelete(AppUser user) {
    showDialog(
      context: context,
      builder: (ctx) {
        final cs = Theme.of(ctx).colorScheme;
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          titlePadding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: cs.errorContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(Icons.delete_outline, color: cs.onErrorContainer, size: 20),
              ),
              const SizedBox(width: 12),
              const Text('Eliminar Usuario', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
            ],
          ),
          content: RichText(
            text: TextSpan(
              style: TextStyle(color: cs.onSurfaceVariant, height: 1.5, fontSize: 14),
              children: [
                const TextSpan(text: '¿Confirmas eliminar a '),
                TextSpan(text: user.shortName, style: TextStyle(color: cs.onSurface, fontWeight: FontWeight.w600)),
                const TextSpan(text: ' ('),
                TextSpan(text: user.email, style: TextStyle(color: cs.primary)),
                const TextSpan(text: ')?\nEsta acción no se puede deshacer.'),
              ],
            ),
          ),
          actionsPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            FilledButton.icon(
              icon: const Icon(Icons.delete_outline, size: 16),
              label: const Text('Eliminar'),
              style: FilledButton.styleFrom(backgroundColor: cs.error, foregroundColor: cs.onError),
              onPressed: () async {
                Navigator.pop(ctx);
                final success = await ref.read(userManagementProvider.notifier).deleteUser(user.id);
                if (success && mounted) {
                  _showSnack('Usuario ${user.shortName} eliminado', isError: false);
                } else if (mounted) {
                  _showSnack('Error al eliminar', isError: true);
                }
              },
            ),
          ],
        );
      },
    );
  }

  void _showSnack(String msg, {required bool isError}) {
    final cs = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(isError ? Icons.error_outline : Icons.check_circle_outline,
                color: isError ? cs.onError : cs.onPrimary, size: 18),
            const SizedBox(width: 10),
            Expanded(child: Text(msg)),
          ],
        ),
        backgroundColor: isError ? cs.error : cs.primary,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(userManagementProvider);
    final cs    = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        backgroundColor: cs.surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Divider(height: 1, thickness: 1, color: cs.outlineVariant.withValues(alpha: 0.5)),
        ),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                color: cs.primaryContainer,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(Icons.manage_accounts_outlined, size: 18, color: cs.onPrimaryContainer),
            ),
            const SizedBox(width: 10),
            Text(
              'Gestión de Usuarios',
              style: TextStyle(
                color: cs.onSurface,
                fontWeight: FontWeight.w700,
                fontSize: 17,
                letterSpacing: -0.3,
              ),
            ),
          ],
        ),
        actions: [
          if (state.isLoading)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: SizedBox(width: 18, height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2, color: cs.primary)),
            ),
          IconButton(
            tooltip: 'Actualizar lista',
            icon: Icon(Icons.refresh_outlined, color: cs.onSurfaceVariant),
            onPressed: () => ref.read(userManagementProvider.notifier).fetchUsers(),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilledButton.icon(
              icon: const Icon(Icons.person_add_outlined, size: 16),
              label: const Text('Nuevo'),
              onPressed: _showAddUserDialog,
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ),
        ],
      ),
      body: _buildBody(state),
    );
  }

  Widget _buildBody(UserManagementState state) {
    final cs = Theme.of(context).colorScheme;

    if (state.isLoading && state.users.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: cs.primary),
            const SizedBox(height: 16),
            Text('Cargando usuarios…', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13)),
          ],
        ),
      );
    }

    if (state.error != null && state.users.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: cs.errorContainer,
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.cloud_off_outlined, size: 36, color: cs.onErrorContainer),
              ),
              const SizedBox(height: 20),
              Text('Error al cargar usuarios',
                  style: TextStyle(color: cs.onSurface, fontWeight: FontWeight.w600, fontSize: 15)),
              const SizedBox(height: 6),
              Text(state.error!, textAlign: TextAlign.center,
                  style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13)),
              const SizedBox(height: 24),
              FilledButton.icon(
                icon: const Icon(Icons.refresh_outlined, size: 16),
                label: const Text('Reintentar'),
                onPressed: () => ref.read(userManagementProvider.notifier).fetchUsers(),
              ),
            ],
          ),
        ),
      );
    }

    if (state.users.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people_outline, size: 56, color: cs.outlineVariant),
            const SizedBox(height: 16),
            Text('Sin usuarios registrados',
                style: TextStyle(color: cs.onSurfaceVariant, fontSize: 14, fontWeight: FontWeight.w500)),
          ],
        ),
      );
    }

    return RefreshIndicator(
      color: cs.primary,
      onRefresh: () => ref.read(userManagementProvider.notifier).fetchUsers(),
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
        itemCount: state.users.length,
        itemBuilder: (context, index) => _UserCard(
          user: state.users[index],
          roleColor: _roleColor(state.users[index].role),
          roleIcon: _roleIcon(state.users[index].role),
          onEdit:   () => _showEditUserDialog(state.users[index]),
          onDelete: () => _confirmDelete(state.users[index]),
        ),
      ),
    );
  }
}


class _UserCard extends StatelessWidget {
  const _UserCard({
    required this.user,
    required this.roleColor,
    required this.roleIcon,
    required this.onEdit,
    required this.onDelete,
  });

  final AppUser  user;
  final Color    roleColor;
  final IconData roleIcon;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    final cs      = Theme.of(context).colorScheme;
    final isActive = user.isActive;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isActive
              ? cs.outlineVariant.withValues(alpha: 0.6)
              : cs.error.withValues(alpha: 0.35),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: cs.shadow.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            // Avatar
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: roleColor.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(roleIcon, color: roleColor, size: 22),
            ),
            const SizedBox(width: 14),
            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Flexible(
                        child: Text(
                          user.shortName,
                          style: TextStyle(
                            color: cs.onSurface,
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                            letterSpacing: -0.2,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      _RoleChip(label: user.roleDisplay, color: roleColor),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user.email,
                    style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12),
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (user.department != null && user.department!.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Icon(Icons.corporate_fare_outlined, size: 11, color: cs.outlineVariant),
                        const SizedBox(width: 3),
                        Text(user.department!,
                            style: TextStyle(color: cs.outlineVariant, fontSize: 11)),
                      ],
                    ),
                  ],
                  if (!isActive) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.block_outlined, size: 11, color: cs.error),
                        const SizedBox(width: 3),
                        Text('Cuenta inactiva',
                            style: TextStyle(color: cs.error, fontSize: 11, fontWeight: FontWeight.w600)),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            // Actions
            PopupMenuButton<String>(
              icon: Icon(Icons.more_vert, color: cs.onSurfaceVariant, size: 20),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              elevation: 4,
              itemBuilder: (_) => [
                PopupMenuItem(
                  value: 'edit',
                  child: Row(
                    children: [
                      Icon(Icons.edit_outlined, size: 16, color: cs.primary),
                      const SizedBox(width: 10),
                      const Text('Editar Usuario'),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: 'delete',
                  child: Row(
                    children: [
                      Icon(Icons.delete_outline, size: 16, color: cs.error),
                      const SizedBox(width: 10),
                      Text('Eliminar Cuenta', style: TextStyle(color: cs.error)),
                    ],
                  ),
                ),
              ],
              onSelected: (val) {
                if (val == 'edit')   onEdit();
                if (val == 'delete') onDelete();
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _RoleChip extends StatelessWidget {
  const _RoleChip({required this.label, required this.color});
  final String label;
  final Color  color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.35), width: 1),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}

class _StyledDialog extends StatelessWidget {
  const _StyledDialog({
    required this.title,
    required this.icon,
    required this.child,
    required this.actions,
    this.subtitle,
  });

  final String       title;
  final IconData     icon;
  final Widget       child;
  final List<Widget> actions;
  final String?      subtitle;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: cs.primaryContainer,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(icon, size: 18, color: cs.onPrimaryContainer),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title,
                          style: TextStyle(
                            color: cs.onSurface,
                            fontWeight: FontWeight.w700,
                            fontSize: 16,
                            letterSpacing: -0.3,
                          )),
                      if (subtitle != null)
                        Text(subtitle!,
                            style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12)),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Flexible(child: SingleChildScrollView(child: child)),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: actions
                    .map((a) => Padding(padding: const EdgeInsets.only(left: 8), child: a))
                    .toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RoleDropdown extends StatelessWidget {
  const _RoleDropdown({
    required this.value,
    required this.roles,
    required this.decoration,
    required this.onChanged,
  });

  final String           value;
  final List<String>     roles;
  final InputDecoration  decoration;
  final ValueChanged<String?> onChanged;

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      value: value,
      decoration: decoration,
      borderRadius: BorderRadius.circular(12),
      items: roles.map((r) => DropdownMenuItem(value: r, child: Text(r, style: const TextStyle(fontSize: 14)))).toList(),
      onChanged: onChanged,
    );
  }
}

class _ActiveToggle extends StatelessWidget {
  const _ActiveToggle({required this.value, required this.onChanged});
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      margin: const EdgeInsets.only(top: 4),
      decoration: BoxDecoration(
        color: cs.surfaceContainerHighest.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: cs.outlineVariant),
      ),
      child: SwitchListTile(
        title: Text('Cuenta activa',
            style: TextStyle(fontSize: 13, color: cs.onSurface, fontWeight: FontWeight.w500)),
        subtitle: Text(value ? 'El usuario puede iniciar sesión' : 'Acceso suspendido',
            style: TextStyle(fontSize: 11, color: value ? cs.primary : cs.error)),
        secondary: Icon(
          value ? Icons.check_circle_outline : Icons.block_outlined,
          color: value ? cs.primary : cs.error,
          size: 20,
        ),
        value: value,
        onChanged: onChanged,
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
        dense: true,
      ),
    );
  }
}
