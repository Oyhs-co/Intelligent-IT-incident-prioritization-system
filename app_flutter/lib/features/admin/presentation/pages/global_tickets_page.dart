import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';
import 'admin_ticket_audit_page.dart';

class GlobalTicketsPage extends ConsumerStatefulWidget {
  const GlobalTicketsPage({super.key});

  @override
  ConsumerState<GlobalTicketsPage> createState() => _GlobalTicketsPageState();
}

class _GlobalTicketsPageState extends ConsumerState<GlobalTicketsPage> {
  String _filter = 'Todos';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(incidentProvider.notifier).fetchIncidents();
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tickets = ref.watch(incidentProvider);

    bool esPrioridadAlta(String? p) {
      final lower = (p ?? '').toLowerCase();
      return lower == 'alta' || lower == 'crítica' || lower == 'critica'
          || lower == 'high' || lower == 'critical';
    }

    final int total = tickets.length;
    final int pendientes = tickets.where((t) => ['pendiente', 'recibido', 'enviando...', 'new', 'open'].contains(t.status.toLowerCase())).length;
    final int resueltos = tickets.where((t) => ['resuelto', 'resolved', 'closed'].contains(t.status.toLowerCase())).length;
    final int criticos = tickets.where((t) => esPrioridadAlta(t.finalPriority ?? t.priorityLabel)).length;

    final displayedTickets = tickets.where((t) {
      if (_filter == 'Pendientes') return ['pendiente', 'recibido', 'enviando...', 'new', 'open'].contains(t.status.toLowerCase());
      if (_filter == 'Resueltos') return ['resuelto', 'resolved', 'closed'].contains(t.status.toLowerCase());
      if (_filter == 'Críticos') return esPrioridadAlta(t.finalPriority ?? t.priorityLabel);
      return true;
    }).toList();

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: const Text('Centro de Monitoreo Global'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Indicadores Clave', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1)),
            const SizedBox(height: 12),
            GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              childAspectRatio: 1.6,
              children: [
                _buildKPICard('Total Activos', total.toString(), Icons.confirmation_number, cs.primary, cs),
                _buildKPICard('Pendientes', pendientes.toString(), Icons.hourglass_empty, const Color(0xFFD97706), cs),
                _buildKPICard('Casos Críticos', criticos.toString(), Icons.warning_rounded, const Color(0xFFDC2626), cs),
                _buildKPICard('Tasa Resolución', total == 0 ? '0%' : '${((resueltos / total) * 100).toInt()}%', Icons.task_alt, const Color(0xFF059669), cs),
              ],
            ),
            const SizedBox(height: 28),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: ['Todos', 'Pendientes', 'Críticos', 'Resueltos'].map((f) => Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(f, style: TextStyle(fontWeight: FontWeight.w600, color: _filter == f ? cs.onPrimary : cs.onSurface)),
                    selected: _filter == f,
                    selectedColor: cs.primary,
                    backgroundColor: cs.surface,
                    onSelected: (val) { if (val) setState(() => _filter = f); },
                  ),
                )).toList(),
              ),
            ),
            const SizedBox(height: 16),
            Text('Registro General de Tickets', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1)),
            const SizedBox(height: 12),
            displayedTickets.isEmpty
                ? Center(child: Padding(padding: const EdgeInsets.all(32), child: Text('No hay tickets que coincidan con el filtro.', style: TextStyle(color: cs.onSurfaceVariant))))
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: displayedTickets.length,
                    itemBuilder: (context, index) {
                      final ticket = displayedTickets[index];
                      final isCritico = esPrioridadAlta(ticket.finalPriority ?? ticket.priorityLabel);

                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        decoration: BoxDecoration(
                          color: cs.surface,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                            color: isCritico ? cs.error.withValues(alpha: 0.3) : cs.outlineVariant.withValues(alpha: 0.6),
                          ),
                        ),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(14),
                          onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => AdminTicketAuditPage(ticket: ticket))),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(10),
                                  decoration: BoxDecoration(
                                    color: isCritico ? cs.errorContainer : cs.primaryContainer,
                                    shape: BoxShape.circle,
                                  ),
                                  child: Icon(
                                    Icons.receipt_long,
                                    color: isCritico ? cs.onErrorContainer : cs.primary,
                                    size: 20,
                                  ),
                                ),
                                const SizedBox(width: 14),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        '${ticket.ticketNumber}: ${ticket.title}',
                                        style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: cs.onSurface),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 4),
                                      Row(
                                        children: [
                                          Text(
                                            ticket.status,
                                            style: TextStyle(
                                              color: ['resuelto', 'resolved', 'closed'].contains(ticket.status.toLowerCase())
                                                  ? const Color(0xFF059669)
                                                  : cs.onSurfaceVariant,
                                              fontWeight: FontWeight.w600,
                                              fontSize: 12,
                                            ),
                                          ),
                                          Text(' • ', style: TextStyle(color: cs.onSurfaceVariant)),
                                          Text(
                                            ticket.category ?? 'Sin asignar',
                                            style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                Icon(Icons.chevron_right, color: cs.onSurfaceVariant),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
          ],
        ),
      ),
    );
  }

  Widget _buildKPICard(String title, String value, IconData icon, Color color, ColorScheme cs) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.02), blurRadius: 6, offset: const Offset(0, 3))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: color, size: 24),
              Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: cs.onSurface)),
            ],
          ),
          Text(title, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
        ],
      ),
    );
  }
}
