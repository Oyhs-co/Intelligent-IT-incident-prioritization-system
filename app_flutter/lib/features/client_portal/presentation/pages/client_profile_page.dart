import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../auth/providers/auth_providers.dart';

class ClientProfilePage extends ConsumerStatefulWidget {
  const ClientProfilePage({super.key});

  @override
  ConsumerState<ClientProfilePage> createState() => _ClientProfilePageState();
}

class _ClientProfilePageState extends ConsumerState<ClientProfilePage> {
  bool notificacionesEmail = true;
  bool notificacionesPush = false;

  late TextEditingController _nameController;
  late TextEditingController _phoneController;

  @override
  void initState() {
    super.initState();
    final user = ref.read(authProvider).user;
    _nameController = TextEditingController(text: user?.fullName ?? user?.username ?? '');
    _phoneController = TextEditingController(text: '+52 555 123 4567');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final user = ref.watch(authProvider).user;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: const Text('Configuración de Usuario'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [cs.primary, cs.primary.withValues(alpha: 0.7)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  (user?.fullName ?? user?.username ?? 'U').substring(0, 1).toUpperCase(),
                  style: TextStyle(fontSize: 36, fontWeight: FontWeight.w700, color: cs.onPrimary),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              user?.fullName ?? user?.username ?? 'Usuario',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: cs.onSurface),
            ),
            Text(
              user?.email ?? '',
              style: TextStyle(color: cs.onSurfaceVariant, fontSize: 14),
            ),
            const SizedBox(height: 32),
            _buildSection(
              cs: cs,
              title: 'Información Personal',
              child: Column(
                children: [
                  TextField(
                    decoration: InputDecoration(
                      labelText: 'Nombre Completo',
                      prefixIcon: const Icon(Icons.badge_outlined, size: 20),
                    ),
                    controller: _nameController,
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    decoration: InputDecoration(
                      labelText: 'Teléfono',
                      prefixIcon: const Icon(Icons.phone_outlined, size: 20),
                    ),
                    controller: _phoneController,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            _buildSection(
              cs: cs,
              title: 'Preferencias de Notificación',
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Notificaciones por Correo'),
                    subtitle: const Text('Recibe alertas sobre el estado de tus tickets.'),
                    value: notificacionesEmail,
                    onChanged: (val) => setState(() => notificacionesEmail = val),
                    activeTrackColor: cs.primary.withValues(alpha: 0.5),
                    activeThumbColor: cs.primary,
                    contentPadding: EdgeInsets.zero,
                  ),
                  Divider(height: 1, color: cs.outlineVariant.withValues(alpha: 0.5)),
                  SwitchListTile(
                    title: const Text('Notificaciones Push'),
                    subtitle: const Text('Recibe alertas en tu dispositivo móvil.'),
                    value: notificacionesPush,
                    onChanged: (val) => setState(() => notificacionesPush = val),
                    activeTrackColor: cs.primary.withValues(alpha: 0.5),
                    activeThumbColor: cs.primary,
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Perfil actualizado correctamente.'),
                      backgroundColor: cs.primary,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                  Navigator.pop(context);
                },
                child: const Text('Guardar Cambios'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({required ColorScheme cs, required String title, required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: cs.onSurface)),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }
}
