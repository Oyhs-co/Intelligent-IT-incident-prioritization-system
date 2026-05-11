import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../../../core/utils/app_translations.dart';
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
    final cs          = Theme.of(context).colorScheme;
    final tickets     = ref.watch(incidentProvider);
    final filter      = ref.watch(technicianFilterProvider);
    final currentUser = ref.watch(authProvider).user;

    // ── Filter logic alineada con el sidebar ─────────────────────────────────
    final filteredTickets = tickets.where((t) {
      if (filter == 'Mis Tickets') {
        return currentUser != null && t.assignedTo == currentUser.id;
      }
      return _matchStatusFilter(t.status, filter);
    }).toList();

    // ── KPI counts ────────────────────────────────────────────────────────────
    final nuevo     = tickets.where((t) => t.status.toLowerCase() == 'new').length;
    final progreso  = tickets.where((t) => t.status.toLowerCase() == 'in_progress').length;
    final resuelto  = tickets.where((t) => ['resolved','closed'].contains(t.status.toLowerCase())).length;

    final title = filter == 'Mis Tickets'
        ? 'Mis Tickets Asignados'
        : 'Tickets${filter != "Todos" ? " · $filter" : ""}';

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      drawer: const ModernSidebar(role: UserRole.technician),
      appBar: AppBar(
        title: Text(title),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            tooltip: 'Actualizar',
            onPressed: () => ref.read(incidentProvider.notifier).fetchIncidents(),
          ),
        ],
      ),
      body: Column(
        children: [
          // ── KPI bar ──────────────────────────────────────────────────────────
          Container(
            color: cs.surface,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: [
                _KpiPill('Nuevos',      nuevo,    const Color(0xFF0D9488)),
                const SizedBox(width: 8),
                _KpiPill('En Progreso', progreso, const Color(0xFF2563EB)),
                const SizedBox(width: 8),
                _KpiPill('Resueltos',   resuelto, const Color(0xFF059669)),
                const Spacer(),
                Text('${tickets.length} total',
                    style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
          Divider(height: 1, color: cs.outlineVariant),

          // ── List or empty state ───────────────────────────────────────────────
          Expanded(
            child: filteredTickets.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.check_circle_outline, size: 64,
                            color: cs.primary.withValues(alpha: 0.4)),
                        const SizedBox(height: 16),
                        Text('¡Sin tickets pendientes!',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: cs.onSurface)),
                        const SizedBox(height: 6),
                        Text(
                          filter == 'Mis Tickets'
                              ? 'No tienes tickets asignados.'
                              : 'No hay tickets con ese estado.',
                          style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13),
                        ),
                      ],
                    ),
                  )
                : RefreshIndicator(
                    color: cs.primary,
                    onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
                    child: _ResponsiveTicketList(tickets: filteredTickets),
                  ),
          ),
        ],
      ),
    );
  }

  // El sidebar usa: Todos / Nuevo / Pendiente / En Progreso / Resuelto / Mis Tickets
  bool _matchStatusFilter(String status, String filter) {
    switch (filter) {
      case 'Nuevo':
        return status.toLowerCase() == 'new';
      case 'Pendiente':
        return status.toLowerCase() == 'pending';
      case 'En Progreso':
        return status.toLowerCase() == 'in_progress';
      case 'Resuelto':
        return ['resolved', 'closed'].contains(status.toLowerCase());
      default: // Todos
        return true;
    }
  }
}

// ── KPI pill ──────────────────────────────────────────────────────────────────

class _KpiPill extends StatelessWidget {
  const _KpiPill(this.label, this.count, this.color);
  final String label;
  final int count;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 6, height: 6, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 5),
          Text('$count $label', style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

// ── Responsive list ───────────────────────────────────────────────────────────

class _ResponsiveTicketList extends StatelessWidget {
  const _ResponsiveTicketList({required this.tickets});
  final List<Incident> tickets;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;

    if (width >= 900) {
      // Wide layout: 3-column grid
      return GridView.builder(
        padding: const EdgeInsets.all(20),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.6,
        ),
        itemCount: tickets.length,
        itemBuilder: (_, i) => _TechnicianTicketCard(ticket: tickets[i]),
      );
    } else if (width >= 600) {
      // Medium layout: 2-column grid
      return GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 10,
          mainAxisSpacing: 10,
          childAspectRatio: 1.5,
        ),
        itemCount: tickets.length,
        itemBuilder: (_, i) => _TechnicianTicketCard(ticket: tickets[i]),
      );
    }

    // Mobile: single column
    return ListView.builder(
      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      itemCount: tickets.length,
      itemBuilder: (_, i) => _TechnicianTicketCard(ticket: tickets[i]),
    );
  }
}

// ── Technician ticket card ────────────────────────────────────────────────────

class _TechnicianTicketCard extends StatelessWidget {
  final Incident ticket;
  const _TechnicianTicketCard({required this.ticket});

  @override
  Widget build(BuildContext context) {
    final cs           = Theme.of(context).colorScheme;
    final priorityLabel = ticket.finalPriority ?? ticket.priorityLabel;
    final pStyle       = AppTranslations.priorityStyle(priorityLabel);
    final sStyle       = AppTranslations.statusStyle(ticket.status);

    return ClipRRect(
      borderRadius: BorderRadius.circular(14),
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        decoration: BoxDecoration(
          color: cs.surface,
          border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.5)),
          boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 3))],
        ),
        child: Stack(
          children: [
            Positioned(left: 0, top: 0, bottom: 0,
              child: Container(width: 4, color: pStyle.accent),
            ),
            InkWell(
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => TechnicianResolvePage(ticket: ticket)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
              // ── Header row ──────────────────────────────────────────────────
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    ticket.ticketNumber,
                    style: TextStyle(color: cs.onSurfaceVariant, fontWeight: FontWeight.w600, fontSize: 12),
                  ),
                  Row(
                    children: [
                      // Status chip
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: sStyle.background,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          AppTranslations.status(ticket.status),
                          style: TextStyle(color: sStyle.text, fontSize: 10, fontWeight: FontWeight.w700),
                        ),
                      ),
                      const SizedBox(width: 6),
                      // Priority chip
                      PriorityChip(priority: priorityLabel),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // ── Title ───────────────────────────────────────────────────────
              Text(
                ticket.title,
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: cs.onSurface),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 6),

              // ── Category + IA ────────────────────────────────────────────────
              Row(
                children: [
                  Icon(Icons.folder_outlined, size: 13, color: cs.onSurfaceVariant),
                  const SizedBox(width: 4),
                  Flexible(
                    child: Text(
                      AppTranslations.category(ticket.category),
                      style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  ...[
                    const SizedBox(width: 10),
                    Icon(Icons.flag_outlined, size: 13, color: pStyle.accent),
                    const SizedBox(width: 3),
                    Flexible(
                      child: Text(
                        AppTranslations.priority(priorityLabel),
                        style: TextStyle(color: pStyle.accent, fontSize: 11, fontWeight: FontWeight.w700),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
        ],
      ),
    ),
  );
  }
}
