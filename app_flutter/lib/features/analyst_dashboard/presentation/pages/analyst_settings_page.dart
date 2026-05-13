import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../auth/providers/auth_providers.dart';

class AnalystSettingsPage extends ConsumerStatefulWidget {
  const AnalystSettingsPage({super.key});

  @override
  ConsumerState<AnalystSettingsPage> createState() => _AnalystSettingsPageState();
}

class _AnalystSettingsPageState extends ConsumerState<AnalystSettingsPage> {
  String status = 'Disponible';

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final user = ref.watch(authProvider).user;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: const Text('Configuración'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: cs.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [cs.primary, cs.primary.withValues(alpha: 0.7)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Center(
                          child: Text(
                            (user?.fullName ?? user?.username ?? 'A').substring(0, 1).toUpperCase(),
                            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: cs.onPrimary),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(user?.fullName ?? user?.username ?? 'Analista', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16, color: cs.onSurface)),
                          Text(user?.email ?? '', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13)),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text('Estado Operativo', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    initialValue: status,
                    items: ['Disponible', 'Ocupado', 'Fuera de la oficina']
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (val) => setState(() => status = val!),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Container(
              decoration: BoxDecoration(
                color: cs.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
              ),
              child: Column(
                children: [
                  ListTile(
                    leading: Icon(Icons.lock_outline, color: cs.onSurfaceVariant),
                    title: Text('Cambiar Contraseña', style: TextStyle(color: cs.onSurface)),
                    trailing: Icon(Icons.arrow_forward_ios, size: 16, color: cs.onSurfaceVariant),
                    onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: const Text('Funcionalidad de cambio de contraseña.'),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    },
                  ),
                  Divider(height: 1, indent: 56, color: cs.outlineVariant.withValues(alpha: 0.5)),
                  ListTile(
                    leading: Icon(Icons.notifications_outlined, color: cs.onSurfaceVariant),
                    title: Text('Ajustes de Notificación', style: TextStyle(color: cs.onSurface)),
                    trailing: Icon(Icons.arrow_forward_ios, size: 16, color: cs.onSurfaceVariant),
                    onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: const Text('Ajustes de notificaciones.'),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
