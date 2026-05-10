import 'package:flutter/material.dart';
import '../../models/incident.dart';

class IncidentDetailsPage extends StatelessWidget {
  final Incident incident;
  const IncidentDetailsPage({super.key, required this.incident});

  static const _statusSteps = [
    'new',
    'open',
    'in_progress',
    'resolved',
    'closed',
  ];

  static const _statusLabels = {
    'new': 'Nuevo',
    'open': 'En revisión',
    'in_progress': 'En progreso',
    'resolved': 'Resuelto',
    'closed': 'Cerrado',
    'rejected': 'Rechazado',
    'pending': 'Pendiente',
  };

  static const _statusMessages = {
    'new': 'Tu reporte ha sido recibido. El equipo lo revisará pronto.',
    'open': 'Un analista está evaluando tu reporte para asignarlo al área correspondiente.',
    'in_progress': 'El equipo técnico está trabajando activamente en la resolución de tu ticket.',
    'resolved': 'El incidente ha sido resuelto. Puedes ver la solución registrada abajo.',
    'closed': 'El ticket ha sido cerrado. Gracias por reportar.',
    'rejected': 'El reporte fue rechazado. Contacta al equipo de soporte para más información.',
  };

  int _statusIndex(String status) {
    final s = status.toLowerCase();
    final idx = _statusSteps.indexOf(s);
    return idx >= 0 ? idx : -1;
  }

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
              _buildHeader(),
              const SizedBox(height: 24),
              _buildDescriptionCard(),
              const SizedBox(height: 24),
              if (_isResolvedOrClosed) _buildResolutionCard(),
              if (_isResolvedOrClosed) const SizedBox(height: 24),
              _buildTimelineCard(),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  bool get _isResolvedOrClosed =>
      ['resolved', 'closed'].contains(incident.status.toLowerCase());

  Widget _buildHeader() {
    final s = incident.status.toLowerCase();
    final label = _statusLabels[s] ?? s;
    final priorityText = incident.priorityLabel ?? incident.finalPriority;

    Color statusColor;
    switch (s) {
      case 'new':
      case 'open':
        statusColor = const Color(0xFF2563EB);
      case 'in_progress':
      case 'pending':
        statusColor = const Color(0xFFD97706);
      case 'resolved':
      case 'closed':
        statusColor = const Color(0xFF10B981);
      default:
        statusColor = const Color(0xFF6B7280);
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'creado ${_formatDate(incident.createdAt)}',
              style: TextStyle(color: Colors.grey.shade500, fontWeight: FontWeight.w500, fontSize: 13),
            ),
            const SizedBox(height: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: statusColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                label.toUpperCase(),
                style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.w800),
              ),
            ),
          ],
        ),
        if (priorityText != null)
          _buildPriorityBadge(priorityText),
      ],
    );
  }

  Widget _buildDescriptionCard() {
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
          const Text('titulo del problema', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280), letterSpacing: 0.5)),
          const SizedBox(height: 8),
          Text(incident.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF111827), letterSpacing: -0.5, height: 1.2)),
          const Padding(padding: EdgeInsets.symmetric(vertical: 24), child: Divider(height: 1, thickness: 1, color: Color(0xFFF3F4F6))),
          const Text('descripcion detallada', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280), letterSpacing: 0.5)),
          const SizedBox(height: 12),
          Text(
            incident.description.isEmpty ? 'sin descripcion.' : incident.description,
            style: const TextStyle(fontSize: 16, color: Color(0xFF374151), height: 1.6),
          ),
          if (incident.category != null && !_isResolvedOrClosed) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFBFDBFE))),
              child: Row(children: [
                const Icon(Icons.info_outline, color: Color(0xFF2563EB), size: 18),
                const SizedBox(width: 10),
                Expanded(child: Text('Asignado al área de ${incident.category}', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600, fontSize: 13))),
              ]),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResolutionCard() {
    final text = incident.resolution ?? incident.finalResolution;
    if (text == null || text.isEmpty) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: const Color(0xFFECFDF5), borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFF10B981))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 24),
          const SizedBox(width: 12),
          const Text('Resolución del Técnico', style: TextStyle(color: Color(0xFF065F46), fontWeight: FontWeight.bold, fontSize: 16)),
        ]),
        const SizedBox(height: 12),
        Text(text, style: const TextStyle(color: Color(0xFF047857), height: 1.5, fontSize: 15)),
      ]),
    );
  }

  Widget _buildTimelineCard() {
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
          const Text('historial de estado', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF111827))),
          const SizedBox(height: 24),
          _buildStatusTimeline(),
        ],
      ),
    );
  }

  Widget _buildStatusTimeline() {
    final currentIdx = _statusIndex(incident.status);
    final steps = _statusSteps;

    return Column(
      children: List.generate(steps.length, (index) {
        final status = steps[index];
        final isCompleted = currentIdx >= index;
        final isCurrent = index == currentIdx;
        final isLast = index == steps.length - 1;
        final label = _statusLabels[status] ?? status;
        final msg = _statusMessages[status] ?? '';

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
                if (!isLast)
                  Container(
                    width: 2,
                    height: isCompleted ? 60 : 40,
                    color: index < currentIdx ? const Color(0xFF2563EB) : const Color(0xFFE5E7EB),
                  ),
              ]),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(top: 0, bottom: 24),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(label,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: isCurrent ? FontWeight.w800 : (isCompleted ? FontWeight.w600 : FontWeight.w500),
                      color: isCurrent ? const Color(0xFF111827) : (isCompleted ? const Color(0xFF374151) : const Color(0xFF9CA3AF)),
                    ),
                  ),
                  if (isCompleted && msg.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(msg,
                      style: TextStyle(
                        fontSize: 13,
                        color: isCurrent ? const Color(0xFF4B5563) : const Color(0xFF9CA3AF),
                        height: 1.4,
                      ),
                    ),
                  ],
                ]),
              ),
            ),
          ],
        );
      }),
    );
  }

  Widget _buildPriorityBadge(String label) {
    Color bgColor, textColor;
    switch (label.toLowerCase()) {
      case 'crítica':
      case 'critica':
      case 'critical':
      case 'p4_critical':
      case 'p4':
        bgColor = const Color(0xFF7F1D1D); textColor = Colors.white; break;
      case 'alta':
      case 'high':
      case 'p3_high':
      case 'p3':
        bgColor = const Color(0xFFFEE2E2); textColor = const Color(0xFF991B1B); break;
      case 'media':
      case 'medium':
      case 'p2_medium':
      case 'p2':
        bgColor = const Color(0xFFFEF3C7); textColor = const Color(0xFF92400E); break;
      default:
        bgColor = const Color(0xFFDEF7EC); textColor = const Color(0xFF03543F);
    }
    final display = label.replaceAll(RegExp(r'^P[1-4]_', caseSensitive: false), '').toUpperCase();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(20)),
      child: Text(display, style: TextStyle(color: textColor, fontSize: 11, fontWeight: FontWeight.w800)),
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
