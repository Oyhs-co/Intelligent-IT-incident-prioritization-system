import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/providers/client_portal_providers.dart';

// Formulario para reportar un incidente.
class NewReportPage extends ConsumerWidget {
  // Controladores para capturar el texto del formulario.
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  NewReportPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nuevo Reporte')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Describe el problema que estás experimentando. Nuestro sistema lo analizará automáticamente.',
              style: TextStyle(fontSize: 16, color: Colors.black54),
            ),
            const SizedBox(height: 20),

            // Campo: titulo corto.
            TextFormField(
              controller: _titleController,
              decoration: const InputDecoration(
                labelText: 'Título corto del problema',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.title),
              ),
            ),
            const SizedBox(height: 20),

            // Campo: descripcion detallada.
            TextFormField(
              controller: _descriptionController,
              maxLines: 5,
              decoration: const InputDecoration(
                labelText: 'Descripción detallada',
                hintText: 'Ej. Mi pantalla no enciende desde esta mañana...',
                border: OutlineInputBorder(),
                alignLabelWithHint: true,
              ),
            ),
            const SizedBox(height: 30),

            // Envia el reporte y vuelve a la lista.
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              onPressed: () {
                ref
                    .read(incidentProvider.notifier)
                    .addIncident(
                      _titleController.text,
                      _descriptionController.text,
                    );

                Navigator.pop(context);
              },
              child: const Text(
                'Enviar Reporte',
                style: TextStyle(fontSize: 18),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
