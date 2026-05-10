import 'package:flutter/material.dart';

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
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        elevation: 0,
        title: const Text('Ajustes de IA', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
              ),
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Auto-asignación inteligente', style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: const Text('La IA asignará el área automáticamente sin pasar por el analista si la confianza es alta.'),
                    value: autoAssign,
                    onChanged: (val) => setState(() => autoAssign = val),
                    activeTrackColor: const Color(0xFF2563EB).withValues(alpha: 0.5),
                    activeThumbColor: const Color(0xFF2563EB),
                  ),
                  const Divider(),
                  SwitchListTile(
                    title: const Text('Modo estricto', style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: const Text('Rechazar tickets que no contengan información técnica suficiente.'),
                    value: strictMode,
                    onChanged: (val) => setState(() => strictMode = val),
                    activeTrackColor: const Color(0xFF2563EB).withValues(alpha: 0.5),
                    activeThumbColor: const Color(0xFF2563EB),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Umbral de Confianza para Prioridad Alta', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 8),
                  Text('Actualmente: ${(priorityThreshold * 100).toInt()}%', style: const TextStyle(color: Colors.grey)),
                  Slider(
                    value: priorityThreshold,
                    min: 0.5,
                    max: 0.99,
                    activeColor: const Color(0xFF2563EB),
                    onChanged: (val) => setState(() => priorityThreshold = val),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Configuración guardada exitosamente.')));
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F172A),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Guardar Cambios', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
