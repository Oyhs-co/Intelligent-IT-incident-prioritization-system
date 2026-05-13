import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:logger/logger.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/utils/app_constants.dart';
import '../../../client_portal/models/incident.dart';
import '../../../client_portal/models/providers/client_portal_providers.dart';

final logger = Logger();

class AdminTicketAuditPage extends ConsumerStatefulWidget {
  final Incident ticket;

  const AdminTicketAuditPage({super.key, required this.ticket});

  @override
  ConsumerState<AdminTicketAuditPage> createState() => _AdminTicketAuditPageState();
}

class _AdminTicketAuditPageState extends ConsumerState<AdminTicketAuditPage> {
  final ApiClient _api = ApiClient();
  List<Map<String, dynamic>> _events = [];
  bool _eventsLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchEvents();
  }

  Future<void> _fetchEvents() async {
    setState(() => _eventsLoading = true);
    try {
      final data = await _api.request('GET', ApiEndpoints.incidentEvents(widget.ticket.id), auth: true);
      if (data is List) {
        _events = data.cast<Map<String, dynamic>>();
      }
    } catch (e) {
      logger.e('Failed to fetch events: $e');
    }
    if (mounted) setState(() => _eventsLoading = false);
  }

  String _eventTypeLabel(String type) {
    switch (type) {
      case 'CREATED': return 'Creado';
      case 'UPDATED': return 'Actualizado';
      case 'STATUS_CHANGED': return 'Cambio de estado';
      case 'PRIORITY_CHANGED': return 'Cambio de prioridad';
      case 'ASSIGNED': return 'Asignado';
      case 'ESCALATED': return 'Escalado';
      case 'RESOLVED': return 'Resuelto';
      case 'CLOSED': return 'Cerrado';
      case 'REOPENED': return 'Reabierto';
      case 'COMMENT_ADDED': return 'Comentario agregado';
      case 'DELETED': return 'Eliminado';
      default: return type;
    }
  }

  IconData _eventIcon(String type) {
    switch (type) {
      case 'CREATED': return Icons.add_circle_outline;
      case 'STATUS_CHANGED': return Icons.swap_horiz;
      case 'PRIORITY_CHANGED': return Icons.flag;
      case 'ASSIGNED': return Icons.person_add;
      case 'ESCALATED': return Icons.warning_amber;
      case 'RESOLVED': return Icons.check_circle_outline;
      case 'CLOSED': return Icons.lock_outline;
      case 'REOPENED': return Icons.replay;
      case 'COMMENT_ADDED': return Icons.comment;
      default: return Icons.circle;
    }
  }

  Color _eventColor(String type) {
    switch (type) {
      case 'CREATED': return const Color(0xFF2563EB);
      case 'STATUS_CHANGED': return const Color(0xFFD97706);
      case 'PRIORITY_CHANGED': return const Color(0xFF7C3AED);
      case 'ASSIGNED': return const Color(0xFF059669);
      case 'ESCALATED': return const Color(0xFFDC2626);
      case 'RESOLVED': return const Color(0xFF10B981);
      case 'CLOSED': return const Color(0xFF6B7280);
      case 'COMMENT_ADDED': return const Color(0xFF6366F1);
      default: return const Color(0xFF94A3B8);
    }
  }

  void _showEditDialog() {
    final titleCtrl = TextEditingController(text: widget.ticket.title);
    final descCtrl = TextEditingController(text: widget.ticket.description);
    final categoryCtrl = TextEditingController(text: widget.ticket.category ?? '');
    final resolutionCtrl = TextEditingController(text: widget.ticket.resolution ?? '');

    String selectedStatus = widget.ticket.status;
    int? selectedPriority = widget.ticket.priority;

    final statuses = ['new', 'open', 'in_progress', 'resolved', 'closed', 'pending', 'rejected'];
    final statusLabels = {
      'new': 'Nuevo', 'open': 'Abierto', 'in_progress': 'En progreso',
      'resolved': 'Resuelto', 'closed': 'Cerrado', 'pending': 'Pendiente', 'rejected': 'Rechazado',
    };
    final priorities = {1: 'Baja', 2: 'Media', 3: 'Alta', 4: 'Crítica'};

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: const Text('Editar Ticket', style: TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: titleCtrl, decoration: const InputDecoration(labelText: 'Título')),
                const SizedBox(height: 8),
                TextField(controller: descCtrl, decoration: const InputDecoration(labelText: 'Descripción'), maxLines: 3),
                const SizedBox(height: 8),
                TextField(controller: categoryCtrl, decoration: const InputDecoration(labelText: 'Categoría')),
                const SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  initialValue: selectedStatus,
                  decoration: const InputDecoration(labelText: 'Estado'),
                  items: statuses.map((s) => DropdownMenuItem(value: s, child: Text(statusLabels[s] ?? s))).toList(),
                  onChanged: (val) => setDialogState(() => selectedStatus = val!),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<int>(
                  initialValue: selectedPriority,
                  decoration: const InputDecoration(labelText: 'Prioridad'),
                  items: priorities.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
                  onChanged: (val) => setDialogState(() => selectedPriority = val),
                ),
                const SizedBox(height: 8),
                TextField(controller: resolutionCtrl, decoration: const InputDecoration(labelText: 'Resolución'), maxLines: 3),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                final body = <String, dynamic>{
                  'title': titleCtrl.text.trim(),
                  'description': descCtrl.text.trim(),
                  'status': selectedStatus,
                  'category': categoryCtrl.text.trim().isEmpty ? null : categoryCtrl.text.trim(),
                  'priority': selectedPriority,
                  'resolution': resolutionCtrl.text.trim().isEmpty ? null : resolutionCtrl.text.trim(),
                };
                final success = await ref.read(incidentProvider.notifier).updateIncident(widget.ticket.id, body);
                if (ctx.mounted) Navigator.pop(ctx);
                if (success && mounted) {
                  ref.read(incidentProvider.notifier).fetchIncidents();
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ticket actualizado'), behavior: SnackBarBehavior.floating));
                } else if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error al actualizar'), backgroundColor: Colors.red, behavior: SnackBarBehavior.floating));
                }
              },
              child: const Text('Guardar Cambios'),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmDelete() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirmar Eliminación', style: TextStyle(fontWeight: FontWeight.bold)),
        content: const Text('¿Estás seguro de que deseas eliminar este ticket del sistema? Esta acción es irreversible.'),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar', style: TextStyle(color: Colors.grey))),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final success = await ref.read(incidentProvider.notifier).deleteIncident(widget.ticket.id);
              if (success && mounted) {
                context.pop();
                ref.read(incidentProvider.notifier).fetchIncidents();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Registro eliminado del sistema.'), backgroundColor: Colors.red, behavior: SnackBarBehavior.floating),
                );
              } else if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Error al eliminar registro'), backgroundColor: Colors.red, behavior: SnackBarBehavior.floating),
                );
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            child: const Text('Eliminar Permanentemente'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final t = widget.ticket;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: Text('Auditoría: ${t.ticketNumber}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            tooltip: 'Editar ticket',
            onPressed: _showEditDialog,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildReportDataCard(t, cs),
            const SizedBox(height: 20),
            _buildActivityTimeline(cs),
            const SizedBox(height: 32),
            _buildDangerZone(cs),
          ],
        ),
      ),
    );
  }

  Widget _buildReportDataCard(Incident t, ColorScheme cs) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Datos del Reporte', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: cs.onSurfaceVariant, letterSpacing: 1)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: cs.primaryContainer, borderRadius: BorderRadius.circular(20)),
                child: Text(
                  _statusLabel(t.status),
                  style: TextStyle(color: cs.primary, fontWeight: FontWeight.bold, fontSize: 11),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(t.title, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: cs.onSurface)),
          const SizedBox(height: 8),
          Text(t.description, style: TextStyle(fontSize: 15, color: cs.onSurface, height: 1.5)),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Divider(height: 1, color: cs.outlineVariant.withValues(alpha: 0.5)),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _AuditMetric(label: 'Prioridad', value: _priorityLabel(t.priority), icon: Icons.flag, cs: cs),
              _AuditMetric(label: 'Categoría', value: t.category ?? 'Sin asignar', icon: Icons.business, cs: cs),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _AuditMetric(label: 'Urgencia', value: '${t.urgency}/5', icon: Icons.speed, cs: cs),
              _AuditMetric(label: 'Impacto', value: '${t.impact}/5', icon: Icons.arrow_circle_down_outlined, cs: cs),
            ],
          ),
          if (t.resolution != null) ...[
            const SizedBox(height: 12),
            _AuditMetric(label: 'Resolución', value: t.resolution!, icon: Icons.description, cs: cs),
          ],
        ],
      ),
    );
  }

  Widget _buildActivityTimeline(ColorScheme cs) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Registro de Actividad', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: cs.surface,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
          ),
          child: _eventsLoading
              ? const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()))
              : _events.isEmpty
                  ? Text('Sin registros de actividad.', style: TextStyle(color: cs.onSurfaceVariant))
                  : Column(
                      children: List.generate(_events.length, (index) {
                        final event = _events[index];
                        final type = event['event_type'] as String? ?? 'UPDATED';
                        final isLast = index == _events.length - 1;
                        final time = event['created_at'] as String? ?? '';

                        return Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Column(
                              children: [
                                Container(
                                  width: 12, height: 12,
                                  margin: const EdgeInsets.only(top: 4),
                                  decoration: BoxDecoration(color: _eventColor(type), shape: BoxShape.circle),
                                ),
                                if (!isLast) Container(width: 2, height: 50, color: _eventColor(type).withValues(alpha: 0.3)),
                              ],
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Padding(
                                padding: const EdgeInsets.only(bottom: 20),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Icon(_eventIcon(type), size: 16, color: _eventColor(type)),
                                        const SizedBox(width: 6),
                                        Text(_eventTypeLabel(type), style: TextStyle(fontWeight: FontWeight.bold, color: _eventColor(type), fontSize: 13)),
                                        const Spacer(),
                                        Text(_formatTime(time), style: TextStyle(color: cs.onSurfaceVariant, fontSize: 11)),
                                      ],
                                    ),
                                    if (event['new_value'] != null || event['old_value'] != null) ...[
                                      const SizedBox(height: 4),
                                      Text(
                                        _eventDetail(event),
                                        style: TextStyle(color: cs.onSurface, fontSize: 13),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ),
                          ],
                        );
                      }),
                    ),
        ),
      ],
    );
  }

  String _eventDetail(Map<String, dynamic> event) {
    final oldVal = event['old_value'] as String?;
    final newVal = event['new_value'] as String?;
    if (oldVal != null && newVal != null) return '$oldVal → $newVal';
    if (newVal != null) return newVal;
    if (oldVal != null) return oldVal;
    return '';
  }

  Widget _buildDangerZone(ColorScheme cs) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Zona de Peligro', style: TextStyle(color: cs.error, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: cs.errorContainer.withValues(alpha: 0.5),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: cs.error.withValues(alpha: 0.4)),
          ),
          child: Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: cs.error, size: 32),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Eliminar Registro', style: TextStyle(fontWeight: FontWeight.bold, color: cs.onErrorContainer, fontSize: 16)),
                    Text('Borrará permanentemente este ticket y su historial.', style: TextStyle(color: cs.onErrorContainer, fontSize: 13)),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              ElevatedButton(
                onPressed: _confirmDelete,
                style: ElevatedButton.styleFrom(
                  backgroundColor: cs.error, foregroundColor: cs.onError,
                  elevation: 0, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: const Text('Eliminar'),
              ),
            ],
          ),
        ),
      ],
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

  String _priorityLabel(int? priority) {
    switch (priority) {
      case 4: return 'Crítica';
      case 3: return 'Alta';
      case 2: return 'Media';
      case 1: return 'Baja';
      default: return 'Sin definir';
    }
  }

  String _formatTime(String iso) {
    try {
      final dt = DateTime.parse(iso);
      return '${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return '';
    }
  }
}

class _AuditMetric extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final ColorScheme cs;

  const _AuditMetric({required this.label, required this.value, required this.icon, required this.cs});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 20, color: cs.onSurfaceVariant),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant, fontWeight: FontWeight.bold)),
            Text(value, style: TextStyle(fontSize: 14, color: cs.onSurface, fontWeight: FontWeight.w600)),
          ],
        ),
      ],
    );
  }
}
