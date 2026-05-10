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

  final areas = ['Redes', 'Soporte de Hardware', 'Cuentas y Accesos', 'Desarrollo de Software', 'Bases de Datos', 'Soporte General'];
  final prioridades = ['Alta', 'Media', 'Baja'];

  @override
  void initState() {
    super.initState();
    areaSeleccionada = widget.ticket.category ?? 'Soporte General';
    prioridadSeleccionada = widget.ticket.finalPriority ?? widget.ticket.priorityLabel ?? 'Media';

    if (!areas.contains(areaSeleccionada)) areas.add(areaSeleccionada);
  }

  Future<void> _classifyWithAI() async {
    setState(() => _isClassifying = true);
    final result = await ref.read(incidentProvider.notifier).classifyIncident(widget.ticket.id);
    if (!mounted) return;
    setState(() => _isClassifying = false);

    if (result != null) {
      final label = result['priority_label'] as String? ?? '';
      areaSeleccionada = label;
      prioridadSeleccionada = label;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Clasificación IA: ${result['priority_label']} (${(result['confidence'] as num? ?? 0).toStringAsFixed(2)})'), backgroundColor: const Color(0xFF059669)),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al clasificar con IA'), backgroundColor: Colors.redAccent),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text('Revisión - ${widget.ticket.ticketNumber}',
          style: const TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18, letterSpacing: -0.5)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
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
                  const Text('TÍTULO DEL PROBLEMA', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 8),
                  Text(widget.ticket.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF111827), height: 1.2)),
                  const Padding(padding: EdgeInsets.symmetric(vertical: 24), child: Divider(height: 1, thickness: 1, color: Color(0xFFF3F4F6))),
                  const Text('DESCRIPCIÓN', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 12),
                  Text(widget.ticket.description, style: const TextStyle(fontSize: 16, color: Color(0xFF374151), height: 1.6)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            Container(
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
                        Text('• Prioridad sugerida: ${widget.ticket.priorityLabel ?? "Sin clasificar"}',
                          style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                        const SizedBox(height: 8),
                        Text('• Confianza: ${widget.ticket.confidenceScore != null ? "${(widget.ticket.confidenceScore! * 100).toInt()}%" : "N/A"}',
                          style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                        if (widget.ticket.explanation != null && widget.ticket.explanation!.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          Text(widget.ticket.explanation!, style: const TextStyle(color: Color(0xFF1E3A8A), fontSize: 13)),
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
            ),
            const SizedBox(height: 24),

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
                  const Text('Decisión del Analista (Triage)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
                  const SizedBox(height: 24),
                  const Text('PRIORIDAD FINAL', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)), contentPadding: const EdgeInsets.symmetric(horizontal: 16)),
                    initialValue: prioridadSeleccionada,
                    items: prioridades.map((p) => DropdownMenuItem(value: p, child: Text(p))).toList(),
                    onChanged: (val) => setState(() => prioridadSeleccionada = val!),
                  ),
                  const SizedBox(height: 24),
                  const Text('ÁREA TÉCNICA ENCARGADA', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)), contentPadding: const EdgeInsets.symmetric(horizontal: 16)),
                    initialValue: areaSeleccionada,
                    items: areas.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
                    onChanged: (val) => setState(() => areaSeleccionada = val!),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            ElevatedButton(
              onPressed: () async {
                await ref.read(incidentProvider.notifier).assignAndEditTicket(widget.ticket.id, areaSeleccionada, prioridadSeleccionada);
                if (context.mounted) Navigator.pop(context);
                if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Ticket asignado a $areaSeleccionada')));
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0F172A),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                elevation: 0,
              ),
              child: const Text('Guardar y Enviar a Área', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
