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
    'open': 'En Revisión',
    'in_progress': 'En Progreso',
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
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: Text(incident.ticketNumber),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(cs),
            const SizedBox(height: 20),
            _buildDescriptionCard(cs),
            const SizedBox(height: 20),
            if (_isResolvedOrClosed) _buildResolutionCard(cs),
            if (_isResolvedOrClosed) const SizedBox(height: 20),
            _buildTimelineCard(cs),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  bool get _isResolvedOrClosed =>
      ['resolved', 'closed'].contains(incident.status.toLowerCase());

  Widget _buildHeader(ColorScheme cs) {
    final s = incident.status.toLowerCase();
    final label = _statusLabels[s] ?? s;
    final priorityText = incident.priorityLabel ?? incident.finalPriority;

    Color statusColor;
    switch (s) {
      case 'new':
      case 'open':
        statusColor = cs.primary;
      case 'in_progress':
      case 'pending':
        statusColor = const Color(0xFFD97706);
      case 'resolved':
      case 'closed':
        statusColor = const Color(0xFF10B981);
      default:
        statusColor = cs.onSurfaceVariant;
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Creado ${_formatDate(incident.createdAt)}',
              style: TextStyle(color: cs.onSurfaceVariant, fontWeight: FontWeight.w500, fontSize: 13),
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

  Widget _buildDescriptionCard(ColorScheme cs) {
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
          Text('Título del Problema', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant, letterSpacing: 0.5)),
          const SizedBox(height: 8),
          Text(incident.title, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: cs.onSurface, letterSpacing: -0.5, height: 1.2)),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 24),
            child: Divider(height: 1, color: cs.outlineVariant.withValues(alpha: 0.5)),
          ),
          Text('Descripción Detallada', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant, letterSpacing: 0.5)),
          const SizedBox(height: 12),
          Text(
            incident.description.isEmpty ? 'Sin descripción.' : incident.description,
            style: TextStyle(fontSize: 16, color: cs.onSurface, height: 1.6),
          ),
          if (incident.category != null && !_isResolvedOrClosed) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: cs.primaryContainer,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: cs.primary.withValues(alpha: 0.3)),
              ),
              child: Row(children: [
                Icon(Icons.info_outline, color: cs.primary, size: 18),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Asignado al área de ${incident.category}',
                    style: TextStyle(color: cs.onPrimaryContainer, fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                ),
              ]),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResolutionCard(ColorScheme cs) {
    final text = incident.resolution ?? incident.finalResolution;
    if (text == null || text.isEmpty) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFFECFDF5),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF10B981)),
      ),
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

  Widget _buildTimelineCard(ColorScheme cs) {
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
          Text('Historial de Estado', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: cs.onSurface)),
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
                padding: const EdgeInsets.only(bottom: 24),
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
