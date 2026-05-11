import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../../client_portal/models/incident.dart';
import '../../../client_portal/models/providers/client_portal_providers.dart';
import '../../../auth/providers/auth_providers.dart';
import '../../models/providers/technician_providers.dart';
import 'technician_resolve_page.dart';

class TechnicianDashboardPage extends ConsumerStatefulWidget {
  const TechnicianDashboardPage({super.key});

  @override
  ConsumerState<TechnicianDashboardPage> createState() => _TechnicianDashboardPageState();
}

class _TechnicianDashboardPageState extends ConsumerState<TechnicianDashboardPage> {
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
    final filter = ref.watch(technicianFilterProvider);
    final currentUser = ref.watch(authProvider).user;

    final filteredTickets = tickets.where((t) {
      final assignedToUser = currentUser != null && t.assignedTo == currentUser.id;
      final statusMatch = _matchStatusFilter(t.status, filter);

      if (filter == 'Mis Tickets') {
        return assignedToUser;
      }
      return statusMatch;
    }).toList();

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      drawer: const ModernSidebar(role: UserRole.technician),
      appBar: AppBar(
        title: Text(
          filter == 'Mis Tickets'
              ? 'Mis Tickets Asignados'
              : 'Tickets del Departamento${filter != "Todos" ? " ($filter)" : ""}',
        ),
      ),
      body: filteredTickets.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle_outline, size: 64, color: cs.primary.withValues(alpha: 0.5)),
                  const SizedBox(height: 16),
                  Text('¡Excelente trabajo!', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  Text(
                    filter == 'Mis Tickets'
                        ? 'No tienes tickets asignados.'
                        : 'No hay tickets con ese estado.',
                    style: TextStyle(color: cs.onSurfaceVariant),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: filteredTickets.length,
                itemBuilder: (context, index) {
                  final ticket = filteredTickets[index];
                  return _TechnicianTicketCard(ticket: ticket);
                },
              ),
            ),
    );
  }

  bool _matchStatusFilter(String status, String filter) {
    switch (filter) {
      case 'Nuevo':
        return status.toLowerCase() == 'new';
      case 'Pendiente':
        return ['new', 'open', 'pending'].contains(status.toLowerCase());
      case 'En Progreso':
        return status.toLowerCase() == 'in_progress';
      case 'Resuelto':
        return ['resolved', 'closed'].contains(status.toLowerCase());
      default:
        return true;
    }
  }
}

class _TechnicianTicketCard extends StatelessWidget {
  final Incident ticket;
  const _TechnicianTicketCard({required this.ticket});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [
          BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4)),
        ],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () {
          Navigator.push(context, MaterialPageRoute(builder: (context) => TechnicianResolvePage(ticket: ticket)));
        },
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    ticket.ticketNumber,
                    style: TextStyle(color: cs.onSurfaceVariant, fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: cs.errorContainer.withValues(alpha: 0.4),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Prioridad ${ticket.finalPriority ?? ticket.priorityLabel ?? "Media"}',
                      style: TextStyle(color: cs.onErrorContainer, fontWeight: FontWeight.w700, fontSize: 11),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                ticket.title,
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.build_circle, size: 16, color: cs.primary),
                  const SizedBox(width: 6),
                  Text(
                    ticket.category ?? 'Área no asignada',
                    style: TextStyle(color: cs.primary, fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                  if (ticket.priorityLabel != null) ...[
                    const SizedBox(width: 16),
                    Icon(Icons.auto_awesome, size: 14, color: cs.primary.withValues(alpha: 0.6)),
                    const SizedBox(width: 4),
                    Text(
                      ticket.priorityLabel!,
                      style: TextStyle(color: cs.primary.withValues(alpha: 0.6), fontSize: 12, fontWeight: FontWeight.w500),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
