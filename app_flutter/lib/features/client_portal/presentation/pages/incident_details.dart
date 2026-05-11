import 'package:flutter/material.dart';
import '../../models/incident.dart';
import '../../../../core/utils/app_translations.dart';

class IncidentDetailsPage extends StatelessWidget {
  final Incident incident;
  const IncidentDetailsPage({super.key, required this.incident});

 

  static const _pipeline = ['new', 'open', 'in_progress', 'resolved', 'closed'];

  static const _pipelineLabels = {
    'new':         'Recibido',
    'open':        'En Revisión',
    'in_progress': 'En Progreso',
    'resolved':    'Resuelto',
    'closed':      'Cerrado',
  };

  static const _pipelineIcons = {
    'new':         Icons.inbox_outlined,
    'open':        Icons.manage_search_outlined,
    'in_progress': Icons.build_outlined,
    'resolved':    Icons.check_circle_outline,
    'closed':      Icons.lock_outline,
  };

  static const _pipelineMessages = {
    'new':         'Tu reporte fue recibido exitosamente y está en cola para revisión.',
    'open':        'Un analista está evaluando tu caso y determinando la prioridad y área.',
    'in_progress': 'El equipo técnico está trabajando activamente en la resolución.',
    'resolved':    '¡Tu incidente fue resuelto! Puedes ver la solución registrada.',
    'closed':      'El ticket fue cerrado. Gracias por tu reporte.',
  };

  bool get _isRejected => incident.status.toLowerCase() == 'rejected';
  bool get _isClosed   => ['resolved', 'closed'].contains(incident.status.toLowerCase());

  int _pipelineIdx() {
    final idx = _pipeline.indexOf(incident.status.toLowerCase());
    return idx >= 0 ? idx : -1;
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final pStyle  = AppTranslations.priorityStyle(incident.finalPriority ?? incident.priorityLabel);
    final sStyle  = AppTranslations.statusStyle(incident.status);

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: Text(incident.ticketNumber),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 40),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
            
              _HeroBanner(
                incident: incident,
                cs: cs,
                sStyle: sStyle,
                pStyle: pStyle,
              ),
              const SizedBox(height: 16),

              
              if (!_isRejected) _PipelineTracker(
                pipeline: _pipeline,
                labels: _pipelineLabels,
                icons: _pipelineIcons,
                messages: _pipelineMessages,
                currentIdx: _pipelineIdx(),
                cs: cs,
              ),
              if (_isRejected) _RejectedBanner(cs: cs),
              const SizedBox(height: 16),

              
              _InfoCard(
                title: 'Descripción del Problema',
                icon: Icons.description_outlined,
                cs: cs,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      incident.title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: cs.onSurface,
                        letterSpacing: -0.3,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      incident.description.isEmpty ? 'Sin descripción adicional.' : incident.description,
                      style: TextStyle(fontSize: 14, color: cs.onSurfaceVariant, height: 1.6),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),

              
              _MetaGrid(incident: incident, cs: cs),
              const SizedBox(height: 12),

              
              if (_isClosed) _ResolutionCard(incident: incident, cs: cs),

              
              if (incident.timeline.isNotEmpty) ...[
                const SizedBox(height: 12),
                _TimelineCard(incident: incident, cs: cs),
              ],
            ],
          ),
        ),
      ),
    );
  }
}



class _HeroBanner extends StatelessWidget {
  const _HeroBanner({
    required this.incident, required this.cs,
    required this.sStyle, required this.pStyle,
  });
  final Incident incident;
  final ColorScheme cs;
  final StatusChipStyle sStyle;
  final PriorityChipStyle pStyle;

  @override
  Widget build(BuildContext context) {
    final isResolved = ['resolved', 'closed'].contains(incident.status.toLowerCase());
    final gradientColors = isResolved
        ? [const Color(0xFF059669), const Color(0xFF0D9488)]
        : [cs.primary, const Color(0xFF7C3AED)];

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: gradientColors,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: gradientColors[0].withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  AppTranslations.status(incident.status).toUpperCase(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
              const Spacer(),
              if (incident.finalPriority != null || incident.priorityLabel != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.white.withValues(alpha: 0.4)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.flag_outlined, color: Colors.white, size: 12),
                      const SizedBox(width: 4),
                      Text(
                        AppTranslations.priority(incident.finalPriority ?? incident.priorityLabel),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            incident.ticketNumber,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            incident.title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.3,
              height: 1.2,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 14),
          Text(
            'Creado el ${_formatDate(incident.createdAt)}',
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
        ],
      ),
    );
  }

  static String _formatDate(String d) {
    try {
      final dt = DateTime.parse(d);
      const months = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
      return '${dt.day} ${months[dt.month - 1]} ${dt.year}';
    } catch (_) {
      return d;
    }
  }
}


class _PipelineTracker extends StatelessWidget {
  const _PipelineTracker({
    required this.pipeline, required this.labels, required this.icons,
    required this.messages, required this.currentIdx, required this.cs,
  });
  final List<String> pipeline;
  final Map<String, String> labels;
  final Map<String, IconData> icons;
  final Map<String, String> messages;
  final int currentIdx;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [
          BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(Icons.timeline_outlined, size: 16, color: cs.primary),
            const SizedBox(width: 8),
            Text(
              'Estado del Ticket',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cs.onSurface),
            ),
          ]),
          const SizedBox(height: 20),
          ...List.generate(pipeline.length, (i) {
            final status  = pipeline[i];
            final done    = currentIdx >= i;
            final current = currentIdx == i;
            final isLast  = i == pipeline.length - 1;

            return IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  
                  SizedBox(
                    width: 36,
                    child: Column(
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          width: current ? 36 : 30,
                          height: current ? 36 : 30,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: done ? cs.primary : cs.surfaceContainerHighest,
                            boxShadow: current
                                ? [BoxShadow(color: cs.primary.withValues(alpha: 0.4), blurRadius: 12, spreadRadius: 2)]
                                : [],
                          ),
                          child: Icon(
                            done ? Icons.check_rounded : (icons[status] ?? Icons.circle_outlined),
                            color: done ? Colors.white : cs.onSurfaceVariant,
                            size: current ? 18 : 15,
                          ),
                        ),
                        if (!isLast)
                          Expanded(
                            child: Container(
                              width: 2,
                              margin: const EdgeInsets.symmetric(vertical: 3),
                              decoration: BoxDecoration(
                                color: i < currentIdx ? cs.primary : cs.outlineVariant,
                                borderRadius: BorderRadius.circular(1),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 14),
                  
                  Expanded(
                    child: Padding(
                      padding: EdgeInsets.only(bottom: isLast ? 0 : 20, top: 4),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            labels[status] ?? status,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: current ? FontWeight.w800 : (done ? FontWeight.w600 : FontWeight.w500),
                              color: current
                                  ? cs.primary
                                  : (done ? cs.onSurface : cs.onSurfaceVariant.withValues(alpha: 0.5)),
                            ),
                          ),
                          if (current && messages[status] != null) ...[
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: cs.primaryContainer.withValues(alpha: 0.5),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                messages[status]!,
                                style: TextStyle(fontSize: 12, color: cs.onSurface, height: 1.4),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}



class _RejectedBanner extends StatelessWidget {
  const _RejectedBanner({required this.cs});
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cs.errorContainer,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.error.withValues(alpha: 0.4)),
      ),
      child: Row(
        children: [
          Icon(Icons.cancel_outlined, color: cs.error, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Ticket Rechazado',
                    style: TextStyle(color: cs.onErrorContainer, fontWeight: FontWeight.w800, fontSize: 15)),
                const SizedBox(height: 4),
                Text(
                  'Tu reporte fue rechazado. Por favor contacta al equipo de soporte para más información.',
                  style: TextStyle(color: cs.onErrorContainer.withValues(alpha: 0.8), fontSize: 12, height: 1.4),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}



class _MetaGrid extends StatelessWidget {
  const _MetaGrid({required this.incident, required this.cs});
  final Incident incident;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    final items = <_MetaItem>[
      _MetaItem(Icons.folder_outlined, 'Categoría', AppTranslations.category(incident.category)),
      _MetaItem(Icons.bolt_outlined, 'Urgencia', '${incident.urgency}/5'),
      _MetaItem(Icons.people_outline, 'Impacto', '${incident.impact}/5'),
      if (incident.confidenceScore != null)
        _MetaItem(Icons.psychology_outlined, 'Confianza IA',
            '${(incident.confidenceScore! * 100).toInt()}%'),
    ];

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      childAspectRatio: 2.8,
      children: items.map((item) => _MetaTile(item: item, cs: cs)).toList(),
    );
  }
}

class _MetaItem {
  const _MetaItem(this.icon, this.label, this.value);
  final IconData icon;
  final String label;
  final String value;
}

class _MetaTile extends StatelessWidget {
  const _MetaTile({required this.item, required this.cs});
  final _MetaItem item;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: cs.primaryContainer.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(item.icon, size: 14, color: cs.primary),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(item.label,
                    style: TextStyle(fontSize: 10, color: cs.onSurfaceVariant, fontWeight: FontWeight.w500)),
                Text(item.value,
                    style: TextStyle(fontSize: 13, color: cs.onSurface, fontWeight: FontWeight.w700),
                    overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        ],
      ),
    );
  }
}



class _ResolutionCard extends StatelessWidget {
  const _ResolutionCard({required this.incident, required this.cs});
  final Incident incident;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    final text = incident.resolution ?? incident.finalResolution;
    if (text == null || text.isEmpty) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF059669), Color(0xFF0D9488)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            const Icon(Icons.verified_outlined, color: Colors.white, size: 20),
            const SizedBox(width: 10),
            const Text('Solución Aplicada',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 15)),
          ]),
          const SizedBox(height: 12),
          Text(text, style: const TextStyle(color: Colors.white, height: 1.5, fontSize: 14)),
        ],
      ),
    );
  }
}



class _TimelineCard extends StatelessWidget {
  const _TimelineCard({required this.incident, required this.cs});
  final Incident incident;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return _InfoCard(
      title: 'Historial de Actividad',
      icon: Icons.history_outlined,
      cs: cs,
      child: Column(
        children: incident.timeline.map((event) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 8, height: 8,
                  margin: const EdgeInsets.only(top: 5, right: 12),
                  decoration: BoxDecoration(color: cs.primary, shape: BoxShape.circle),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(event.title,
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: cs.onSurface)),
                      const SizedBox(height: 2),
                      Text(event.description,
                          style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant, height: 1.4)),
                    ],
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}



class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.title, required this.icon, required this.cs, required this.child});
  final String title;
  final IconData icon;
  final ColorScheme cs;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 3))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(icon, size: 15, color: cs.primary),
            const SizedBox(width: 8),
            Text(title, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: cs.onSurface)),
          ]),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }
}
