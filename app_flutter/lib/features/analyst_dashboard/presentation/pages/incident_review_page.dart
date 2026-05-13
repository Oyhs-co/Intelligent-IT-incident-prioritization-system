import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../features/client_portal/models/incident.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';
import '../../models/providers/analyst_metadata_providers.dart';

class IncidentReviewPage extends ConsumerStatefulWidget {
  final Incident ticket;

  const IncidentReviewPage({super.key, required this.ticket});

  @override
  ConsumerState<IncidentReviewPage> createState() => _IncidentReviewPageState();
}

class _IncidentReviewPageState extends ConsumerState<IncidentReviewPage> {
  String? _selectedCategoryValue;
  int? _selectedPriorityValue;
  bool _isClassifying = false;
  bool _metadataLoaded = false;

  Incident get _incident =>
      ref.watch(incidentProvider).where((i) => i.id == widget.ticket.id).firstOrNull ?? widget.ticket;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadMetadata();
    });
  }

  Future<void> _loadMetadata() async {
    final notifier = ref.read(metadataProvider.notifier);
    if (ref.read(metadataProvider).categories.isEmpty) {
      await notifier.fetchMetadata();
    }
    if (mounted) {
      setState(() {
        _metadataLoaded = true;
        _initSelections();
      });
    }
  }

  void _initSelections() {
    final meta = ref.read(metadataProvider);
    final inc = _incident;

    if (inc.category != null) {
      final match = meta.categories.where((c) => c.value == inc.category).firstOrNull;
      _selectedCategoryValue = match?.value ?? (meta.categories.isNotEmpty ? meta.categories.first.value : null);
    } else {
      _selectedCategoryValue = meta.categories.isNotEmpty ? meta.categories.first.value : null;
    }

    if (inc.priority != null) {
      _selectedPriorityValue = inc.priority;
    } else {
      _selectedPriorityValue = meta.priorities.isNotEmpty ? meta.priorities.first.value : null;
    }
  }

  String _findCategoryLabel(String? value) {
    final meta = ref.read(metadataProvider);
    final match = meta.categories.where((c) => c.value == value).firstOrNull;
    return match?.label ?? value ?? 'Sin asignar';
  }

  String _findPriorityLabel(int? value) {
    final meta = ref.read(metadataProvider);
    final match = meta.priorities.where((p) => p.value == value).firstOrNull;
    return match?.label ?? value?.toString() ?? 'Sin definir';
  }

  Future<void> _classifyWithAI() async {
    setState(() => _isClassifying = true);
    final result = await ref.read(incidentProvider.notifier).classifyIncident(widget.ticket.id);
    if (!mounted) return;
    setState(() => _isClassifying = false);

    if (result != null) {
      final priorityVal = result['priority'] as int?;
      if (priorityVal != null) {
        setState(() => _selectedPriorityValue = priorityVal);
      }
      final label = result['priority_label'] as String? ?? '';
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Clasificación IA: $label (${(result['confidence'] as num? ?? 0).toStringAsFixed(2)})'),
            backgroundColor: const Color(0xFF059669),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al clasificar con IA'), backgroundColor: Colors.redAccent, behavior: SnackBarBehavior.floating),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final inc = _incident;
    final meta = ref.watch(metadataProvider);
    final categories = meta.categories;
    final priorities = meta.priorities;
    final isLoading = meta.isLoading && !_metadataLoaded;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: Text('Revisión - ${inc.ticketNumber}'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildDescriptionCard(inc, cs),
            const SizedBox(height: 20),
            _buildAIAnalysisCard(inc, cs),
            const SizedBox(height: 20),
            _buildMetadataCard(inc, cs),
            const SizedBox(height: 20),
            _buildTriageCard(categories, priorities, isLoading, cs),
            const SizedBox(height: 28),
            _buildSubmitButton(cs),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildDescriptionCard(Incident inc, ColorScheme cs) {
    return Container(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(inc.ticketNumber, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: cs.onSurfaceVariant)),
              _buildStatusChip(inc.status, cs),
            ],
          ),
          const SizedBox(height: 16),
          Text('Título del Problema', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
          const SizedBox(height: 8),
          Text(inc.title, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: cs.onSurface, height: 1.2)),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 24),
            child: Divider(height: 1, color: cs.outlineVariant.withValues(alpha: 0.5)),
          ),
          Text('Descripción', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
          const SizedBox(height: 12),
          Text(inc.description, style: TextStyle(fontSize: 16, color: cs.onSurface, height: 1.6)),
        ],
      ),
    );
  }

  Widget _buildAIAnalysisCard(Incident inc, ColorScheme cs) {
    return Container(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.primary.withValues(alpha: 0.3), width: 1.5),
        boxShadow: [BoxShadow(color: cs.primary.withValues(alpha: 0.05), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_awesome, color: cs.primary),
              const SizedBox(width: 8),
              Text('Análisis de IA', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: cs.primaryContainer, borderRadius: BorderRadius.circular(10)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('• Prioridad sugerida: ${inc.priorityLabel ?? "Sin clasificar"}',
                  style: TextStyle(fontWeight: FontWeight.w600, color: cs.onPrimaryContainer)),
                const SizedBox(height: 8),
                Text('• Confianza: ${inc.confidenceScore != null ? "${(inc.confidenceScore! * 100).toInt()}%" : "N/A"}',
                  style: TextStyle(fontWeight: FontWeight.w600, color: cs.onPrimaryContainer)),
                if (inc.explanation != null && inc.explanation!.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(inc.explanation!, style: TextStyle(color: cs.onPrimaryContainer, fontSize: 13)),
                ],
                if (inc.status == 'open')
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Row(
                      children: [
                        Icon(Icons.check_circle, size: 14, color: const Color(0xFF059669)),
                        const SizedBox(width: 6),
                        Text('Estado actualizado a Abierto', style: TextStyle(color: const Color(0xFF059669), fontSize: 12, fontWeight: FontWeight.w600)),
                      ],
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: _isClassifying ? null : _classifyWithAI,
              icon: _isClassifying
                  ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.auto_awesome),
              label: Text(_isClassifying ? 'Clasificando...' : 'Clasificar con IA'),
              style: OutlinedButton.styleFrom(
                foregroundColor: cs.primary,
                side: BorderSide(color: cs.primary),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetadataCard(Incident inc, ColorScheme cs) {
    return Container(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Detalles del Ticket', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
          const SizedBox(height: 20),
          _metadataRow('Estado', inc.status, cs),
          _metadataRow('Urgencia', '${inc.urgency}/5', cs),
          _metadataRow('Impacto', '${inc.impact}/5', cs),
          _metadataRow('Categoría', _findCategoryLabel(inc.category), cs),
          _metadataRow('Subcategoría', inc.subcategory ?? 'Sin asignar', cs),
          _metadataRow('Fuente', inc.source, cs),
          _metadataRow('Creado', inc.createdAt.length >= 10 ? inc.createdAt.substring(0, 10) : inc.createdAt, cs),
          _metadataRow('Actualizado', inc.updatedAt.length >= 10 ? inc.updatedAt.substring(0, 10) : inc.updatedAt, cs),
          if (inc.slaDeadline != null)
            _metadataRow('SLA Límite', inc.slaDeadline!.length >= 10 ? inc.slaDeadline!.substring(0, 10) : inc.slaDeadline!, cs),
          if (inc.assignedTo != null) _metadataRow('Asignado a', inc.assignedTo!, cs),
          if (inc.isSlaBreached)
            Container(
              margin: const EdgeInsets.only(top: 12),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(color: cs.errorContainer, borderRadius: BorderRadius.circular(8)),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.warning_amber_rounded, color: cs.error, size: 18),
                  const SizedBox(width: 8),
                  Text('SLA incumplido', style: TextStyle(color: cs.error, fontWeight: FontWeight.w700, fontSize: 13)),
                ],
              ),
            ),
          if (inc.tags.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text('Tags', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: inc.tags.map((t) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: cs.surfaceContainerHighest, borderRadius: BorderRadius.circular(20)),
                child: Text(t, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurface)),
              )).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _metadataRow(String label, String value, ColorScheme cs) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
          ),
          Expanded(
            child: Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: cs.onSurface)),
          ),
        ],
      ),
    );
  }

  Widget _buildTriageCard(List<IncidentCategory> categories, List<PriorityOption> priorities, bool isLoading, ColorScheme cs) {
    return Container(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Decisión del Analista (Triage)', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
          const SizedBox(height: 24),
          Text('Prioridad Final', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
          const SizedBox(height: 8),
          if (isLoading || priorities.isEmpty)
            const SizedBox(height: 56, child: Center(child: CircularProgressIndicator(strokeWidth: 2)))
          else
            DropdownButtonFormField<int>(
              decoration: InputDecoration(
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16),
              ),
              initialValue: _selectedPriorityValue ?? (priorities.isNotEmpty ? priorities.first.value : null),
              items: priorities.map((p) => DropdownMenuItem(value: p.value, child: Text('${p.label} (${p.value})'))).toList(),
              onChanged: (val) => setState(() => _selectedPriorityValue = val),
            ),
          const SizedBox(height: 24),
          Text('Departamento / Área Técnica', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
          const SizedBox(height: 8),
          if (isLoading || categories.isEmpty)
            const SizedBox(height: 56, child: Center(child: CircularProgressIndicator(strokeWidth: 2)))
          else
            DropdownButtonFormField<String>(
              decoration: InputDecoration(
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16),
              ),
              initialValue: _selectedCategoryValue ?? (categories.isNotEmpty ? categories.first.value : null),
              items: categories.map((c) => DropdownMenuItem(value: c.value, child: Text(c.label))).toList(),
              onChanged: (val) => setState(() => _selectedCategoryValue = val),
            ),
        ],
      ),
    );
  }

  Widget _buildSubmitButton(ColorScheme cs) {
    final canSubmit = _selectedCategoryValue != null && _selectedPriorityValue != null;

    return ElevatedButton(
      onPressed: canSubmit
          ? () async {
              final catLabel = _findCategoryLabel(_selectedCategoryValue);
              final messenger = ScaffoldMessenger.of(context);
              final router = GoRouter.of(context);
              await ref.read(incidentProvider.notifier).assignAndEditTicket(
                widget.ticket.id,
                _selectedCategoryValue!,
                _selectedPriorityValue!,
              );
              if (!context.mounted) return;
              router.pop();
              messenger.showSnackBar(SnackBar(
                content: Text('Ticket asignado a $catLabel con prioridad ${_findPriorityLabel(_selectedPriorityValue)}'),
                backgroundColor: cs.primary,
                behavior: SnackBarBehavior.floating,
              ));
            }
          : null,
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF0F172A),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        elevation: 0,
      ),
      child: const Text('Guardar y Enviar a Departamento', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
    );
  }

  Widget _buildStatusChip(String status, ColorScheme cs) {
    Color bgColor;
    Color textColor;
    switch (status.toLowerCase()) {
      case 'resolved':
      case 'closed':
        bgColor = const Color(0xFFDEF7EC);
        textColor = const Color(0xFF03543F);
        break;
      case 'in_progress':
      case 'pending':
        bgColor = const Color(0xFFE1EFFE);
        textColor = const Color(0xFF1E429F);
        break;
      case 'open':
        bgColor = const Color(0xFFE0E7FF);
        textColor = const Color(0xFF4338CA);
        break;
      case 'rejected':
        bgColor = const Color(0xFFFEE2E2);
        textColor = const Color(0xFF991B1B);
        break;
      default:
        bgColor = const Color(0xFFFEF3C7);
        textColor = const Color(0xFF92400E);
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(20)),
      child: Text(
        _statusLabel(status),
        style: TextStyle(color: textColor, fontSize: 11, fontWeight: FontWeight.w800),
      ),
    );
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'new': return 'NUEVO';
      case 'open': return 'ABIERTO';
      case 'in_progress': return 'EN PROGRESO';
      case 'resolved': return 'RESUELTO';
      case 'closed': return 'CERRADO';
      case 'pending': return 'PENDIENTE';
      case 'rejected': return 'RECHAZADO';
      default: return status.toUpperCase();
    }
  }
}
