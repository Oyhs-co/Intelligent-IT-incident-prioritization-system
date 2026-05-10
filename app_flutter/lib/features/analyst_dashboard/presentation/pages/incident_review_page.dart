import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/incident.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';

class IncidentReviewPage extends ConsumerStatefulWidget {
  final Incident ticket;

  const IncidentReviewPage({super.key, required this.ticket});

  @override
  ConsumerState<IncidentReviewPage> createState() => _IncidentReviewPageState();
}

class _IncidentReviewPageState extends ConsumerState<IncidentReviewPage> {
  late String areaSeleccionada;
  late String prioridadSeleccionada;
  bool _isClassifying = false;

  static const _areas = ['Redes', 'Soporte de Hardware', 'Cuentas y Accesos', 'Desarrollo de Software', 'Bases de Datos', 'Soporte General'];
  static const _prioridades = ['Crítica', 'Alta', 'Media', 'Baja'];

  static const _priorityValue = {
    'Crítica': 4,
    'Alta': 3,
    'Media': 2,
    'Baja': 1,
  };

  Incident get _incident =>
      ref.watch(incidentProvider).where((i) => i.id == widget.ticket.id).firstOrNull ?? widget.ticket;

  @override
  void initState() {
    super.initState();
    areaSeleccionada = widget.ticket.category ?? 'Soporte General';
    prioridadSeleccionada = _matchPriorityLabel(widget.ticket.finalPriority ?? widget.ticket.priorityLabel);

    if (!_areas.contains(areaSeleccionada)) areaSeleccionada = 'Soporte General';
  }

  String _matchPriorityLabel(String? label) {
    if (label == null) return 'Media';
    final lower = label.toLowerCase();
    if (lower == 'crítica' || lower == 'critica' || lower == 'critical' || lower == 'p4 (critical)') return 'Crítica';
    if (lower == 'alta' || lower == 'high' || lower == 'p3 (high)') return 'Alta';
    if (lower == 'media' || lower == 'medium' || lower == 'p2 (medium)') return 'Media';
    if (lower == 'baja' || lower == 'low' || lower == 'p1 (low)') return 'Baja';
    return 'Media';
  }

  Future<void> _classifyWithAI() async {
    setState(() => _isClassifying = true);
    final result = await ref.read(incidentProvider.notifier).classifyIncident(widget.ticket.id);
    if (!mounted) return;
    setState(() => _isClassifying = false);

    if (result != null) {
      final label = result['priority_label'] as String? ?? '';
      prioridadSeleccionada = _matchPriorityLabel(label);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Clasificación IA: $label (${(result['confidence'] as num? ?? 0).toStringAsFixed(2)})'),
            backgroundColor: const Color(0xFF059669),
          ),
        );
      }
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al clasificar con IA'), backgroundColor: Colors.redAccent),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final inc = _incident;

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text('Revisión - ${inc.ticketNumber}',
          style: const TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18, letterSpacing: -0.5)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildDescriptionCard(inc),
            const SizedBox(height: 24),
            _buildAIAnalysisCard(inc),
            const SizedBox(height: 24),
            _buildMetadataCard(inc),
            const SizedBox(height: 24),
            _buildTriageCard(),
            const SizedBox(height: 32),
            _buildSubmitButton(),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildDescriptionCard(Incident inc) {
    return Container(
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(inc.ticketNumber, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF6B7280), letterSpacing: 0.5)),
              _buildStatusChip(inc.status),
            ],
          ),
          const SizedBox(height: 16),
          const Text('TÍTULO DEL PROBLEMA', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
          const SizedBox(height: 8),
          Text(inc.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF111827), height: 1.2)),
          const Padding(padding: EdgeInsets.symmetric(vertical: 24), child: Divider(height: 1, thickness: 1, color: Color(0xFFF3F4F6))),
          const Text('DESCRIPCIÓN', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
          const SizedBox(height: 12),
          Text(inc.description, style: const TextStyle(fontSize: 16, color: Color(0xFF374151), height: 1.6)),
        ],
      ),
    );
  }

  Widget _buildAIAnalysisCard(Incident inc) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF2563EB).withValues(alpha: 0.2), width: 1.5),
        boxShadow: [BoxShadow(color: const Color(0xFF2563EB).withValues(alpha: 0.05), blurRadius: 12, offset: const Offset(0, 6))],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.auto_awesome, color: Color(0xFF2563EB)),
              const SizedBox(width: 8),
              const Text('Análisis de IA', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(8)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('• Prioridad sugerida: ${inc.priorityLabel ?? "Sin clasificar"}',
                  style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                const SizedBox(height: 8),
                Text('• Confianza: ${inc.confidenceScore != null ? "${(inc.confidenceScore! * 100).toInt()}%" : "N/A"}',
                  style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                if (inc.explanation != null && inc.explanation!.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(inc.explanation!, style: const TextStyle(color: Color(0xFF1E3A8A), fontSize: 13)),
                ],
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
                foregroundColor: const Color(0xFF2563EB),
                side: const BorderSide(color: Color(0xFF2563EB)),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetadataCard(Incident inc) {
    return Container(
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
          const Text('Detalles del Ticket', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
          const SizedBox(height: 20),
          _metadataRow('Estado', inc.status),
          _metadataRow('Urgencia', '${inc.urgency}/5'),
          _metadataRow('Impacto', '${inc.impact}/5'),
          _metadataRow('Categoría', inc.category ?? 'Sin asignar'),
          _metadataRow('Subcategoría', inc.subcategory ?? 'Sin asignar'),
          _metadataRow('Fuente', inc.source),
          _metadataRow('Creado', inc.createdAt.length >= 10 ? inc.createdAt.substring(0, 10) : inc.createdAt),
          _metadataRow('Actualizado', inc.updatedAt.length >= 10 ? inc.updatedAt.substring(0, 10) : inc.updatedAt),
          if (inc.slaDeadline != null)
            _metadataRow('SLA Límite', inc.slaDeadline!.length >= 10 ? inc.slaDeadline!.substring(0, 10) : inc.slaDeadline!),
          if (inc.assignedTo != null) _metadataRow('Asignado a', inc.assignedTo!),
          if (inc.isSlaBreached)
            Container(
              margin: const EdgeInsets.only(top: 12),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(color: Colors.red.shade50, borderRadius: BorderRadius.circular(8)),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.warning_amber_rounded, color: Colors.red, size: 18),
                  SizedBox(width: 8),
                  Text('SLA incumplido', style: TextStyle(color: Colors.red, fontWeight: FontWeight.w700, fontSize: 13)),
                ],
              ),
            ),
          if (inc.tags.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text('Tags', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: inc.tags.map((t) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: const Color(0xFFF3F4F6), borderRadius: BorderRadius.circular(20)),
                child: Text(t, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF374151))),
              )).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _metadataRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: Color(0xFF111827))),
          ),
        ],
      ),
    );
  }

  Widget _buildTriageCard() {
    return Container(
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
          const Text('Decisión del Analista (Triage)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
          const SizedBox(height: 24),
          const Text('PRIORIDAD FINAL', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)), contentPadding: const EdgeInsets.symmetric(horizontal: 16)),
            initialValue: prioridadSeleccionada,
            items: _prioridades.map((p) => DropdownMenuItem(value: p, child: Text(p))).toList(),
            onChanged: (val) => setState(() => prioridadSeleccionada = val!),
          ),
          const SizedBox(height: 24),
          const Text('ÁREA TÉCNICA ENCARGADA', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)), contentPadding: const EdgeInsets.symmetric(horizontal: 16)),
            initialValue: areaSeleccionada,
            items: _areas.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
            onChanged: (val) => setState(() => areaSeleccionada = val!),
          ),
        ],
      ),
    );
  }

  Widget _buildSubmitButton() {
    return ElevatedButton(
      onPressed: () async {
        final messenger = ScaffoldMessenger.of(context);
        final navigator = Navigator.of(context);
        await ref.read(incidentProvider.notifier).assignAndEditTicket(
          widget.ticket.id,
          areaSeleccionada,
          prioridadSeleccionada,
          priorityValue: _priorityValue[prioridadSeleccionada],
        );
        if (!context.mounted) {
          return;
        }
        navigator.pop();
        messenger.showSnackBar(SnackBar(content: Text('Ticket asignado a $areaSeleccionada')));
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF0F172A),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        elevation: 0,
      ),
      child: const Text('Guardar y Enviar a Área', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
    );
  }

  Widget _buildStatusChip(String status) {
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
        status.toUpperCase(),
        style: TextStyle(color: textColor, fontSize: 11, fontWeight: FontWeight.w800),
      ),
    );
  }
}
