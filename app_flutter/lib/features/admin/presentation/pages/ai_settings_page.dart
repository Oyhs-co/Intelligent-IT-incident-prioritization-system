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
        title: const Text('Ajustes del Modelo IA', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            
            // Comportamiento del Modelo
            const Text('COMPORTAMIENTO DEL MODELO', style: TextStyle(color: Colors.black54, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.05)),
              ),
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Auto-asignación inteligente', style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: const Text('La IA asignará el área automáticamente si la confianza supera el umbral establecido.'),
                    value: autoAssign,
                    onChanged: (val) => setState(() => autoAssign = val),
                    activeTrackColor: const Color(0xFF2563EB).withValues(alpha: 0.5),
                    activeThumbColor: const Color(0xFF2563EB),
                    secondary: const Icon(Icons.auto_awesome, color: Color(0xFF2563EB)),
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Modo estricto', style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: const Text('Requerir confirmación manual del Analista para tickets críticos.'),
                    value: strictMode,
                    onChanged: (val) => setState(() => strictMode = val),
                    activeTrackColor: const Color(0xFF2563EB).withValues(alpha: 0.5),
                    activeThumbColor: const Color(0xFF2563EB),
                    secondary: const Icon(Icons.security, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Sensibilidad
            const Text('SENSIBILIDAD DE PRIORIDAD', style: TextStyle(color: Colors.black54, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.05)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Expanded(
                        child: Text(
                          'Umbral de Confianza para Prioridad Alta', 
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text('${(priorityThreshold * 100).toInt()}%', style: const TextStyle(color: Color(0xFF2563EB), fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Slider(
                    value: priorityThreshold,
                    min: 0.5,
                    max: 0.99,
                    activeColor: const Color(0xFF2563EB),
                    inactiveColor: const Color(0xFFE2E8F0),
                    onChanged: (val) => setState(() => priorityThreshold = val),
                  ),
                  const Text('Valores más bajos clasifican más tickets como urgentes. Valores altos son más conservadores.', style: TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Configuración guardada en la base de datos.')));
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F172A),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Guardar Configuración', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
