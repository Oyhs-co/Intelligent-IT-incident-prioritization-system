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
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text('nuevo reporte', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18, letterSpacing: -0.5)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text('¿que problema estas experimentando?',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: Color(0xFF111827), letterSpacing: -0.5)),
              const SizedBox(height: 8),
              const Text('nuestro sistema lo analizara automaticamente y te daremos respuesta lo mas pronto posible.',
                style: TextStyle(fontSize: 15, color: Color(0xFF6B7280), height: 1.5)),
              const SizedBox(height: 32),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
                  boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 12, offset: const Offset(0, 6))],
                ),
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('titulo corto del problema', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF374151))),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _titleController,
                      enabled: !_isLoading,
                      decoration: InputDecoration(
                        hintText: 'ej. error de conexion a la red...',
                        filled: true,
                        fillColor: const Color(0xFFF9FAFB),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 1.5)),
                        prefixIcon: const Icon(Icons.title, color: Color(0xFF9CA3AF), size: 20),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                      ),
                    ),
                    const SizedBox(height: 24),

                    const Text('descripcion detallada', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF374151))),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _descriptionController,
                      enabled: !_isLoading,
                      maxLines: 5,
                      decoration: InputDecoration(
                        hintText: 'describe los pasos que seguiste, mensajes de error, etc.',
                        filled: true,
                        fillColor: const Color(0xFFF9FAFB),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 1.5)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                      ),
                    ),
                    const SizedBox(height: 24),

                    const Text('categoria (opcional)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF374151))),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      initialValue: _category,
                      decoration: InputDecoration(
                        filled: true,
                        fillColor: const Color(0xFFF9FAFB),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                      ),
                      items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(_categoryLabels[c]!))).toList(),
                      onChanged: (val) => setState(() => _category = val ?? ''),
                    ),
                    const SizedBox(height: 24),

                    const Text('urgencia (1-5)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF374151))),
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

                    const Text('impacto (1-5)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF374151))),
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
              const SizedBox(height: 32),

              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  backgroundColor: const Color(0xFF0F172A),
                  foregroundColor: Colors.white,
                  elevation: 2,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
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
                      content: Text(success ? 'ticket enviado con exito.' : 'error al enviar el ticket.'),
                      backgroundColor: success ? const Color(0xFF059669) : const Color(0xFFD97706),
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                  if (success) Navigator.pop(context);
                },
                child: _isLoading
                    ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                    : const Text('enviar reporte', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, letterSpacing: 0.5)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
