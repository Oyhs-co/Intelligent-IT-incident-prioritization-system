import 'package:flutter/material.dart';

class AnalystDirectoryPage extends StatelessWidget {
  const AnalystDirectoryPage({super.key});

  @override
  Widget build(BuildContext context) {
    final areas = [
      {'name': 'Redes', 'status': 'Disponible', 'color': Colors.green},
      {'name': 'Soporte de Hardware', 'status': 'Ocupado', 'color': Colors.orange},
      {'name': 'Cuentas y Accesos', 'status': 'Disponible', 'color': Colors.green},
      {'name': 'Desarrollo de Software', 'status': 'Alta Demanda', 'color': Colors.red},
      {'name': 'Bases de Datos', 'status': 'Disponible', 'color': Colors.green},
      {'name': 'Soporte General', 'status': 'Disponible', 'color': Colors.green},
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text('Directorio Técnico', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800)),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: areas.length,
        itemBuilder: (context, index) {
          final area = areas[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: Colors.black.withValues(alpha: 0.08)),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: (area['color'] as Color).withValues(alpha: 0.1), shape: BoxShape.circle),
                child: Icon(Icons.lan, color: area['color'] as Color),
              ),
              title: Text(area['name'] as String, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('Estado actual: ${area['status']}', style: TextStyle(color: area['color'] as Color, fontWeight: FontWeight.w600)),
            ),
          );
        },
      ),
    );
  }
}
