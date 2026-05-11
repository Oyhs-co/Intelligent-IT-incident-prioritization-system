import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/providers/client_portal_providers.dart';

class NewReportPage extends ConsumerStatefulWidget {
  const NewReportPage({super.key});

  @override
  ConsumerState<NewReportPage> createState() => _NewReportPageState();
}

class _NewReportPageState extends ConsumerState<NewReportPage> {
  final _formKey            = GlobalKey<FormState>();
  final _titleController    = TextEditingController();
  final _descriptionController = TextEditingController();
  int    _urgency  = 3;
  int    _impact   = 3;
  String _category = '';
  bool   _isLoading = false;

  final _categories = ['', 'hardware', 'software', 'network', 'security', 'other'];
  final _categoryLabels = {
    '':         'Sin categoría',
    'hardware': 'Hardware',
    'software': 'Software',
    'network':  'Red',
    'security': 'Seguridad',
    'other':    'Otro',
  };
  final _categoryIcons = {
    '':         Icons.category_outlined,
    'hardware': Icons.memory_outlined,
    'software': Icons.code_outlined,
    'network':  Icons.wifi_outlined,
    'security': Icons.security_outlined,
    'other':    Icons.help_outline,
  };

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  

  String? _validateTitle(String? v) {
    if (v == null || v.trim().isEmpty) return 'El título es requerido';
    if (v.trim().length < 5) return 'El título debe tener al menos 5 caracteres';
    if (v.trim().length > 120) return 'El título no puede superar 120 caracteres';
    return null;
  }

  String? _validateDescription(String? v) {
    if (v == null || v.trim().isEmpty) return 'La descripción es requerida';
    if (v.trim().length < 20) return 'Describe el problema con al menos 20 caracteres';
    return null;
  }

  

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    final success = await ref.read(incidentProvider.notifier).createIncident(
      title:       _titleController.text.trim(),
      description: _descriptionController.text.trim(),
      category:    _category.isEmpty ? null : _category,
      urgency:     _urgency,
      impact:      _impact,
    );
    if (!mounted) return;
    setState(() => _isLoading = false);

    final cs = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(children: [
          Icon(
            success ? Icons.check_circle_outline : Icons.error_outline,
            color: Colors.white, size: 18,
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(
            success ? 'Reporte enviado exitosamente.' : 'Error al enviar el reporte.',
            style: const TextStyle(color: Colors.white, fontSize: 13),
          )),
        ]),
        backgroundColor: success ? const Color(0xFF059669) : cs.error,
        margin: const EdgeInsets.all(16),
      ),
    );
    if (success) Navigator.pop(context);
  }


  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(title: const Text('Nuevo Reporte'), centerTitle: true),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [cs.primaryContainer, cs.tertiaryContainer],
                    begin: Alignment.topLeft, end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    Icon(Icons.report_outlined, size: 36, color: cs.onPrimaryContainer),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('¿Qué problema tienes?',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: cs.onPrimaryContainer)),
                          const SizedBox(height: 4),
                          Text('Nuestro sistema lo analizará y te dará respuesta pronto.',
                              style: TextStyle(fontSize: 12, color: cs.onPrimaryContainer.withValues(alpha: 0.8), height: 1.4)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              
              _SectionCard(
                title: 'Detalle del Incidente',
                icon: Icons.description_outlined,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TextFormField(
                      controller: _titleController,
                      enabled: !_isLoading,
                      validator: _validateTitle,
                      autovalidateMode: AutovalidateMode.onUserInteraction,
                      decoration: const InputDecoration(
                        labelText: 'Título del problema',
                        hintText: 'Ej. No puedo conectarme a la red',
                        prefixIcon: Icon(Icons.title_outlined, size: 18),
                      ),
                    ),
                    const SizedBox(height: 14),
                    TextFormField(
                      controller: _descriptionController,
                      enabled: !_isLoading,
                      maxLines: 5,
                      validator: _validateDescription,
                      autovalidateMode: AutovalidateMode.onUserInteraction,
                      decoration: const InputDecoration(
                        labelText: 'Descripción detallada',
                        hintText: 'Describe los pasos, mensajes de error, cuándo ocurrió…',
                        alignLabelWithHint: true,
                        prefixIcon: Padding(
                          padding: EdgeInsets.only(bottom: 60),
                          child: Icon(Icons.notes_outlined, size: 18),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              
              _SectionCard(
                title: 'Categoría',
                icon: Icons.folder_outlined,
                child: _CategoryGrid(
                  selected: _category,
                  categories: _categories,
                  labels: _categoryLabels,
                  icons: _categoryIcons,
                  onSelected: (c) => setState(() => _category = c),
                  cs: cs,
                ),
              ),
              const SizedBox(height: 14),

              
              _SectionCard(
                title: 'Severidad',
                icon: Icons.warning_amber_outlined,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _LevelSelector(
                      label: 'Urgencia',
                      value: _urgency,
                      onChanged: (v) => setState(() => _urgency = v),
                      cs: cs,
                    ),
                    const SizedBox(height: 16),
                    _LevelSelector(
                      label: 'Impacto',
                      value: _impact,
                      onChanged: (v) => setState(() => _impact = v),
                      cs: cs,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              
              _isLoading
                  ? Container(
                      height: 52,
                      decoration: BoxDecoration(
                        color: cs.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: SizedBox(width: 22, height: 22,
                            child: CircularProgressIndicator(strokeWidth: 2.5, color: cs.primary)),
                      ),
                    )
                  : FilledButton.icon(
                      onPressed: _submit,
                      icon: const Icon(Icons.send_outlined, size: 18),
                      label: const Text('Enviar Reporte'),
                    ),
            ],
          ),
        ),
      ),
    );
  }
}



class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.icon, required this.child});
  final String title;
  final IconData icon;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.7)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 3))],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(icon, size: 16, color: cs.primary),
            const SizedBox(width: 8),
            Text(title, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cs.onSurface)),
          ]),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }
}



class _CategoryGrid extends StatelessWidget {
  const _CategoryGrid({
    required this.selected, required this.categories, required this.labels,
    required this.icons, required this.onSelected, required this.cs,
  });
  final String selected;
  final List<String> categories;
  final Map<String, String> labels;
  final Map<String, IconData> icons;
  final ValueChanged<String> onSelected;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8, runSpacing: 8,
      children: categories.where((c) => c.isNotEmpty).map((c) {
        final isSelected = selected == c;
        return GestureDetector(
          onTap: () => onSelected(isSelected ? '' : c),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: isSelected ? cs.primaryContainer : cs.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: isSelected ? cs.primary : cs.outlineVariant,
                width: isSelected ? 1.5 : 1,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icons[c], size: 14, color: isSelected ? cs.primary : cs.onSurfaceVariant),
                const SizedBox(width: 6),
                Text(labels[c]!,
                    style: TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w600,
                      color: isSelected ? cs.primary : cs.onSurfaceVariant,
                    )),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }
}



class _LevelSelector extends StatelessWidget {
  const _LevelSelector({required this.label, required this.value, required this.onChanged, required this.cs});
  final String label;
  final int value;
  final ValueChanged<int> onChanged;
  final ColorScheme cs;

  static const _levelColors = [
    Color(0xFF059669), // 1 - low
    Color(0xFF16A34A), // 2
    Color(0xFFD97706), // 3 - medium
    Color(0xFFDC2626), // 4 - high
    Color(0xFF991B1B), // 5 - critical
  ];
  static const _levelLabels = ['Muy Baja', 'Baja', 'Media', 'Alta', 'Crítica'];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurface)),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
              decoration: BoxDecoration(
                color: _levelColors[value - 1].withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: _levelColors[value - 1].withValues(alpha: 0.4)),
              ),
              child: Text(
                _levelLabels[value - 1],
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: _levelColors[value - 1]),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: List.generate(5, (i) {
            final v = i + 1;
            final isSelected = value == v;
            return Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 3),
                child: GestureDetector(
                  onTap: () => onChanged(v),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    height: 36,
                    decoration: BoxDecoration(
                      color: isSelected ? _levelColors[i] : _levelColors[i].withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isSelected ? _levelColors[i] : _levelColors[i].withValues(alpha: 0.3),
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        '$v',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w800,
                          color: isSelected ? Colors.white : _levelColors[i],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            );
          }),
        ),
      ],
    );
  }
}
