import 'package:flutter/material.dart';
import '../../models/incident.dart';

class IncidentDetailsPage extends StatelessWidget {
  final Incident incident;
  const IncidentDetailsPage({super.key, required this.incident});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text(
          incident.ticketNumber,
          style: const TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18, letterSpacing: -0.5),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('creado ${_formatDate(incident.createdAt)}', style: TextStyle(color: Colors.grey.shade500, fontWeight: FontWeight.w500, fontSize: 13)),
                  if (incident.priorityLabel != null) _buildPriorityBadge(incident.priorityLabel!),
                ],
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
                    const Text('titulo del problema', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280), letterSpacing: 0.5)),
                    const SizedBox(height: 8),
                    Text(incident.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF111827), letterSpacing: -0.5, height: 1.2)),
                    const Padding(padding: EdgeInsets.symmetric(vertical: 24), child: Divider(height: 1, thickness: 1, color: Color(0xFFF3F4F6))),
                    const Text('descripcion detallada', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280), letterSpacing: 0.5)),
                    const SizedBox(height: 12),
                    Text(incident.description.isEmpty ? 'sin descripcion.' : incident.description,
                      style: const TextStyle(fontSize: 16, color: Color(0xFF374151), height: 1.6)),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              if (incident.confidenceScore != null || incident.priorityLabel != null)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFBFDBFE)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(children: [Icon(Icons.auto_awesome, color: Color(0xFF2563EB), size: 18), SizedBox(width: 8), Text('Analisis de IA', style: TextStyle(fontWeight: FontWeight.w700, color: Color(0xFF1E3A8A), fontSize: 14))]),
                      const SizedBox(height: 12),
                      if (incident.priorityLabel != null) Text('Prioridad: ${incident.priorityLabel}', style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                      if (incident.confidenceScore != null) Text('Confianza: ${(incident.confidenceScore! * 100).toInt()}%', style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                      if (incident.explanation != null && incident.explanation!.isNotEmpty) ...[const SizedBox(height: 8), Text(incident.explanation!, style: const TextStyle(color: Color(0xFF1E3A8A), fontSize: 13, height: 1.4))],
                    ],
                  ),
                ),
              if (incident.confidenceScore != null || incident.priorityLabel != null) const SizedBox(height: 24),

              if (incident.category != null && !['resolved', 'closed', 'resuelto'].contains(incident.status.toLowerCase()))
                Column(children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFBFDBFE))),
                    child: Row(children: [
                      const Icon(Icons.info_outline, color: Color(0xFF2563EB)),
                      const SizedBox(width: 12),
                      Expanded(child: Text('Tu reporte ha sido asignado al área de ${incident.category}.', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600, height: 1.4))),
                    ]),
                  ),
                  const SizedBox(height: 24),
                ]),

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
                    const Text('historial de estado', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF111827))),
                    const SizedBox(height: 24),
                    _buildTimeline(incident),
                  ],
                ),
              ),

              if (['resolved', 'closed', 'resuelto'].contains(incident.status.toLowerCase()) && incident.finalResolution != null) ...[
                const SizedBox(height: 24),
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(color: const Color(0xFFECFDF5), borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFF10B981))),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Row(children: [const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 24), const SizedBox(width: 12), const Text('Reporte de Resolución del Técnico', style: TextStyle(color: Color(0xFF065F46), fontWeight: FontWeight.bold, fontSize: 16))]),
                    const SizedBox(height: 12),
                    Text(incident.finalResolution!, style: const TextStyle(color: Color(0xFF047857), height: 1.5, fontSize: 15)),
                  ]),
                ),
              ],
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPriorityBadge(String label) {
    Color bgColor, textColor;
    switch (label.toLowerCase()) {
      case 'critical': bgColor = const Color(0xFFFEE2E2); textColor = const Color(0xFF991B1B); break;
      case 'high': bgColor = const Color(0xFFFFEDD5); textColor = const Color(0xFF9A3412); break;
      case 'medium': bgColor = const Color(0xFFFEF3C7); textColor = const Color(0xFF92400E); break;
      default: bgColor = const Color(0xFFDEF7EC); textColor = const Color(0xFF03543F);
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(20)),
      child: Text(label.toUpperCase(), style: TextStyle(color: textColor, fontSize: 11, fontWeight: FontWeight.w800)),
    );
  }

  Widget _buildTimeline(Incident incident) {
    if (incident.timeline.isNotEmpty) {
      return Column(
        children: List.generate(incident.timeline.length, (index) {
          final event = incident.timeline[index];
          final isLast = index == incident.timeline.length - 1;
          final isCurrent = isLast;

          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 16,
                child: Column(children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    width: isCurrent ? 16 : 12,
                    height: isCurrent ? 16 : 12,
                    margin: const EdgeInsets.only(top: 4),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFF2563EB),
                      border: isCurrent ? Border.all(color: const Color(0xFFBFDBFE), width: 4) : null,
                    ),
                  ),
                  if (!isLast) Container(width: 2, height: 60, color: const Color(0xFF2563EB)),
                ]),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 24),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                      Text(event.title, style: TextStyle(fontSize: 15, fontWeight: isCurrent ? FontWeight.w800 : FontWeight.w600, color: const Color(0xFF111827))),
                      Text('${event.date.hour}:${event.date.minute.toString().padLeft(2, '0')}', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                    ]),
                    const SizedBox(height: 4),
                    Text(event.description, style: const TextStyle(fontSize: 13, color: Color(0xFF4B5563), height: 1.4)),
                  ]),
                ),
              ),
            ],
          );
        }),
      );
    }

    final states = [
      {'title': 'nuevo', 'desc': 'El reporte ha sido creado y está a la espera de ser revisado.'},
      {'title': 'abierto', 'desc': 'El reporte ha sido recibido y el equipo lo está analizando.'},
      {'title': 'en progreso', 'desc': 'El equipo técnico está trabajando activamente en la resolución.'},
      {'title': 'resuelto', 'desc': 'El incidente ha sido resuelto de manera exitosa.'},
    ];

    final normalized = incident.status.toLowerCase();
    final statusMap = {'new': 'nuevo', 'open': 'abierto', 'in_progress': 'en progreso', 'pending': 'en progreso', 'resolved': 'resuelto', 'closed': 'resuelto'};
    final displayStatus = statusMap[normalized] ?? normalized;
    int currentIndex = states.indexWhere((s) => s['title'] == displayStatus);
    if (currentIndex == -1) currentIndex = 0;

    return Column(
      children: List.generate(states.length, (index) {
        final isCompleted = index <= currentIndex;
        final isCurrent = index == currentIndex;
        final isLast = index == states.length - 1;

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 16,
              child: Column(children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  width: isCurrent ? 16 : 12,
                  height: isCurrent ? 16 : 12,
                  margin: const EdgeInsets.only(top: 4),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isCompleted ? const Color(0xFF2563EB) : const Color(0xFFE5E7EB),
                    border: isCurrent ? Border.all(color: const Color(0xFFBFDBFE), width: 4) : null,
                  ),
                ),
                if (!isLast) Container(width: 2, height: isCompleted ? 60 : 40, color: index < currentIndex ? const Color(0xFF2563EB) : const Color(0xFFE5E7EB)),
              ]),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(top: 0, bottom: 24),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(states[index]['title']!,
                    style: TextStyle(fontSize: 15, fontWeight: isCurrent ? FontWeight.w800 : (isCompleted ? FontWeight.w600 : FontWeight.w500),
                      color: isCurrent ? const Color(0xFF111827) : (isCompleted ? const Color(0xFF374151) : const Color(0xFF9CA3AF)))),
                  if (isCompleted) ...[const SizedBox(height: 4), Text(states[index]['desc']!,
                    style: TextStyle(fontSize: 13, color: isCurrent ? const Color(0xFF4B5563) : const Color(0xFF9CA3AF), height: 1.4))],
                ]),
              ),
            ),
          ],
        );
      }),
    );
  }

  String _formatDate(String dateStr) {
    try {
      final dt = DateTime.parse(dateStr);
      return '${dt.day}/${dt.month}/${dt.year}';
    } catch (_) {
      return dateStr;
    }
  }
}
