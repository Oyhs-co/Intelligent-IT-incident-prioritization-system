import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/providers/client_portal_providers.dart';

class NewReportPage extends ConsumerStatefulWidget {
  const NewReportPage({super.key});

  @override
  ConsumerState<NewReportPage> createState() => _NewReportPageState();
}

class _NewReportPageState extends ConsumerState<NewReportPage> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  int _urgency = 3;
  int _impact = 3;
  String _category = '';
  bool _isLoading = false;

  final _categories = ['', 'hardware', 'software', 'network', 'security', 'other'];
  final _categoryLabels = {'': 'Sin categoría', 'hardware': 'Hardware', 'software': 'Software', 'network': 'Red', 'security': 'Seguridad', 'other': 'Otro'};

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: const Text('Nuevo Reporte'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              '¿Qué problema estás experimentando?',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: cs.onSurface, letterSpacing: -0.5),
            ),
            const SizedBox(height: 8),
            Text(
              'Nuestro sistema lo analizará automáticamente y te daremos respuesta lo más pronto posible.',
              style: TextStyle(fontSize: 15, color: cs.onSurfaceVariant, height: 1.5),
            ),
            const SizedBox(height: 28),

            Container(
              decoration: BoxDecoration(
                color: cs.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
                boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4))],
              ),
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Título del Problema', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _titleController,
                    enabled: !_isLoading,
                    decoration: const InputDecoration(
                      hintText: 'Ej. Error de conexión a la red...',
                      prefixIcon: Icon(Icons.title, size: 20),
                    ),
                  ),
                  const SizedBox(height: 24),

                  Text('Descripción Detallada', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _descriptionController,
                    enabled: !_isLoading,
                    maxLines: 5,
                    decoration: const InputDecoration(
                      hintText: 'Describe los pasos que seguiste, mensajes de error, etc.',
                      alignLabelWithHint: true,
                    ),
                  ),
                  const SizedBox(height: 24),

                  Text('Categoría (Opcional)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    initialValue: _category,
                    items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(_categoryLabels[c]!))).toList(),
                    onChanged: (val) => setState(() => _category = val ?? ''),
                  ),
                  const SizedBox(height: 24),

                  Text('Urgencia (1-5)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  Row(
                    children: List.generate(5, (i) {
                      final val = i + 1;
                      return Expanded(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 2),
                          child: ChoiceChip(
                            label: Text('$val', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                            selected: _urgency == val,
                            selectedColor: val >= 4 ? Colors.red.shade100 : (val >= 3 ? Colors.orange.shade100 : Colors.green.shade100),
                            onSelected: (_) => setState(() => _urgency = val),
                          ),
                        ),
                      );
                    }),
                  ),
                  const SizedBox(height: 24),

                  Text('Impacto (1-5)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  Row(
                    children: List.generate(5, (i) {
                      final val = i + 1;
                      return Expanded(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 2),
                          child: ChoiceChip(
                            label: Text('$val', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                            selected: _impact == val,
                            selectedColor: val >= 4 ? Colors.red.shade100 : (val >= 3 ? Colors.orange.shade100 : Colors.green.shade100),
                            onSelected: (_) => setState(() => _impact = val),
                          ),
                        ),
                      );
                    }),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            ElevatedButton(
              onPressed: _isLoading ? null : () async {
                setState(() => _isLoading = true);
                final success = await ref.read(incidentProvider.notifier).createIncident(
                  title: _titleController.text,
                  description: _descriptionController.text,
                  category: _category.isEmpty ? null : _category,
                  urgency: _urgency,
                  impact: _impact,
                );
                if (!context.mounted) return;
                setState(() => _isLoading = false);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success ? 'Ticket enviado con éxito.' : 'Error al enviar el ticket.'),
                    backgroundColor: success ? const Color(0xFF059669) : const Color(0xFFD97706),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
                if (success) Navigator.pop(context);
              },
              child: _isLoading
                  ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                  : const Text('Enviar Reporte'),
            ),
          ],
        ),
      ),
    );
  }
}
