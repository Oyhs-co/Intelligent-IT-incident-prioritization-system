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
  Widget build(BuildContext context) {
    final tickets = ref.watch(incidentProvider);

    final int total = tickets.length;
    final int pendientes = tickets.where((t) => ['pendiente', 'recibido', 'enviando...', 'new', 'open'].contains(t.status.toLowerCase())).length;
    final int resueltos = tickets.where((t) => ['resuelto', 'resolved', 'closed'].contains(t.status.toLowerCase())).length;
    final int criticos = tickets.where((t) => (t.finalPriority ?? t.priorityLabel ?? '').toLowerCase() == 'alta' || (t.finalPriority ?? t.priorityLabel ?? '').toLowerCase() == 'crítica').length;

    final displayedTickets = tickets.where((t) {
      if (_filter == 'Pendientes') return ['pendiente', 'recibido', 'enviando...', 'new', 'open'].contains(t.status.toLowerCase());
      if (_filter == 'Resueltos') return ['resuelto', 'resolved', 'closed'].contains(t.status.toLowerCase());
      if (_filter == 'Críticos') return (t.finalPriority ?? t.priorityLabel ?? '').toLowerCase() == 'alta' || (t.finalPriority ?? t.priorityLabel ?? '').toLowerCase() == 'crítica';
      return true;
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        elevation: 0,
        title: const Text('Centro de Monitoreo Global', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('INDICADORES CLAVE', style: TextStyle(color: Colors.black54, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            const SizedBox(height: 12),
            GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              childAspectRatio: 1.5,
              children: [
                _buildKPICard('Total Activos', total.toString(), Icons.confirmation_number, Colors.blue),
                _buildKPICard('Pendientes', pendientes.toString(), Icons.hourglass_empty, Colors.orange),
                _buildKPICard('Casos Críticos', criticos.toString(), Icons.warning_rounded, Colors.red),
                _buildKPICard('Tasa Resolución', total == 0 ? '0%' : '${((resueltos / total) * 100).toInt()}%', Icons.task_alt, Colors.green),
              ],
            ),
            const SizedBox(height: 32),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: ['Todos', 'Pendientes', 'Críticos', 'Resueltos'].map((f) => Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(f, style: TextStyle(fontWeight: FontWeight.bold, color: _filter == f ? Colors.white : Colors.black87)),
                    selected: _filter == f,
                    selectedColor: const Color(0xFF2563EB),
                    backgroundColor: Colors.white,
                    onSelected: (val) { if (val) setState(() => _filter = f); },
                  ),
                )).toList(),
              ),
            ),
            const SizedBox(height: 16),
            const Text('REGISTRO GENERAL DE TICKETS', style: TextStyle(color: Colors.black54, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            const SizedBox(height: 12),
            displayedTickets.isEmpty
                ? const Center(child: Padding(padding: EdgeInsets.all(32), child: Text('No hay tickets que coincidan con el filtro.')))
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: displayedTickets.length,
                    itemBuilder: (context, index) {
                      final ticket = displayedTickets[index];
                      final priorityText = (ticket.finalPriority ?? ticket.priorityLabel ?? '').toLowerCase();
                      final isCritico = priorityText == 'alta' || priorityText == 'crítica' || priorityText == 'critical';

                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                          side: BorderSide(color: isCritico ? Colors.red.withValues(alpha: 0.3) : Colors.black.withValues(alpha: 0.05)),
                        ),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(16),
                          onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => AdminTicketAuditPage(ticket: ticket))),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(10),
                                  decoration: BoxDecoration(color: isCritico ? const Color(0xFFFEF2F2) : const Color(0xFFEFF6FF), shape: BoxShape.circle),
                                  child: Icon(Icons.receipt_long, color: isCritico ? Colors.red : const Color(0xFF2563EB)),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text('${ticket.ticketNumber}: ${ticket.title}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF111827)), maxLines: 1, overflow: TextOverflow.ellipsis),
                                      const SizedBox(height: 4),
                                      Row(
                                        children: [
                                          Text(ticket.status, style: TextStyle(color: ['resuelto', 'resolved', 'closed'].contains(ticket.status.toLowerCase()) ? Colors.green : Colors.grey, fontWeight: FontWeight.bold, fontSize: 12)),
                                          const Text(' • ', style: TextStyle(color: Colors.grey)),
                                          Text(ticket.category ?? 'Sin asignar', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                const Icon(Icons.chevron_right, color: Colors.grey),
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

  Widget _buildKPICard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.05)),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.02), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: color, size: 24),
              Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFF111827))),
            ],
          ),
          Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.grey)),
        ],
      ),
    );
  }
}
