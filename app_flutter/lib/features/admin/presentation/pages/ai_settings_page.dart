import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class AISettingsPage extends StatefulWidget {
  const AISettingsPage({super.key});

  @override
  State<AISettingsPage> createState() => _AISettingsPageState();
}

class _AISettingsPageState extends State<AISettingsPage> {
  bool autoAssign = true;
  bool strictMode = false;
  double priorityThreshold = 0.75;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: const Text('Ajustes del Modelo IA'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Comportamiento del Modelo', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1)),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: cs.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
              ),
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Auto-asignación Inteligente', style: TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: const Text('La IA asignará el área automáticamente si la confianza supera el umbral.'),
                    value: autoAssign,
                    onChanged: (val) => setState(() => autoAssign = val),
                    activeTrackColor: cs.primary.withValues(alpha: 0.5),
                    activeThumbColor: cs.primary,
                    secondary: Icon(Icons.auto_awesome, color: cs.primary),
                  ),
                  Divider(height: 1, indent: 56, color: cs.outlineVariant.withValues(alpha: 0.5)),
                  SwitchListTile(
                    title: const Text('Modo Estricto', style: TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: const Text('Requerir confirmación manual del analista para tickets críticos.'),
                    value: strictMode,
                    onChanged: (val) => setState(() => strictMode = val),
                    activeTrackColor: cs.primary.withValues(alpha: 0.5),
                    activeThumbColor: cs.primary,
                    secondary: Icon(Icons.security, color: cs.onSurfaceVariant),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text('Sensibilidad de Prioridad', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1)),
            const SizedBox(height: 8),
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
                      Expanded(
                        child: Text('Umbral de Confianza para Prioridad Alta',
                          style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: cs.onSurface)),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: cs.primaryContainer,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text('${(priorityThreshold * 100).toInt()}%', style: TextStyle(color: cs.primary, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Slider(
                    value: priorityThreshold,
                    min: 0.5,
                    max: 0.99,
                    activeColor: cs.primary,
                    inactiveColor: cs.surfaceContainerHighest,
                    onChanged: (val) => setState(() => priorityThreshold = val),
                  ),
                  Text(
                    'Valores más bajos clasifican más tickets como urgentes. Valores altos son más conservadores.',
                    style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12),
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
                      content: const Text('Configuración guardada correctamente.'),
                      backgroundColor: cs.primary,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                  context.pop();
                },
                child: const Text('Guardar Configuración'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
