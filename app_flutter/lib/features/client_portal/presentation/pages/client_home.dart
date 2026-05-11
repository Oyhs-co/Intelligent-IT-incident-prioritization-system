import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'new_report.dart';
import '../../models/providers/client_portal_providers.dart';
import 'incident_details.dart';
import '../../models/incident.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../../../core/utils/app_translations.dart';

class ClientHome extends ConsumerStatefulWidget {
  const ClientHome({super.key});

  @override
  ConsumerState<ClientHome> createState() => _ClientHomeState();
}

class _ClientHomeState extends ConsumerState<ClientHome> {
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
    final todosLosTickets = ref.watch(incidentProvider);
    final filtroActual = ref.watch(clientFilterProvider);

    final listaDeTickets = filtroActual == 'Todos'
        ? todosLosTickets
        : todosLosTickets.where((t) => _matchFilter(t.status, filtroActual)).toList();

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      drawer: const ModernSidebar(),
      appBar: AppBar(
        title: Text(
          'Mis Incidentes${filtroActual != "Todos" ? " ($filtroActual)" : ""}',
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
        child: listaDeTickets.isEmpty
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.inbox_outlined, size: 64, color: cs.outlineVariant),
                    const SizedBox(height: 16),
                    Text('No tienes incidentes reportados.', style: TextStyle(color: cs.onSurfaceVariant)),
                  ],
                ),
              )
            : LayoutBuilder(
                builder: (context, constraints) {
                  final width = constraints.maxWidth;
                  if (width >= 900) {
                    return GridView.builder(
                      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 3,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                        childAspectRatio: 1.7,
                      ),
                      itemCount: listaDeTickets.length,
                      itemBuilder: (_, i) => _ModernTicketCard(ticket: listaDeTickets[i]),
                    );
                  } else if (width >= 600) {
                    return GridView.builder(
                      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 10,
                        mainAxisSpacing: 10,
                        childAspectRatio: 1.6,
                      ),
                      itemCount: listaDeTickets.length,
                      itemBuilder: (_, i) => _ModernTicketCard(ticket: listaDeTickets[i]),
                    );
                  }
                  return ListView.builder(
                    physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                    padding: const EdgeInsets.only(top: 8, bottom: 80),
                    itemCount: listaDeTickets.length,
                    itemBuilder: (_, i) => _ModernTicketCard(ticket: listaDeTickets[i]),
                  );
                },
              ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(context, MaterialPageRoute(builder: (context) => const NewReportPage()));
        },
        elevation: 2,
        backgroundColor: cs.primary,
        foregroundColor: cs.onPrimary,
        icon: const Icon(Icons.add_rounded, size: 20),
        label: const Text('Nuevo Reporte', style: TextStyle(fontWeight: FontWeight.w600)),
      ),
    );
  }

  bool _matchFilter(String status, String filter) {
    switch (filter.toLowerCase()) {
      case 'pendiente':
        return ['new', 'open', 'pending'].contains(status.toLowerCase());
      case 'en progreso':
        return status.toLowerCase() == 'in_progress';
      case 'resuelto':
        return ['resolved', 'closed'].contains(status.toLowerCase());
      default:
        return true;
    }
  }
}

class _ModernTicketCard extends StatelessWidget {
  final Incident ticket;
  const _ModernTicketCard({required this.ticket});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
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
          Navigator.push(context, MaterialPageRoute(builder: (context) => IncidentDetailsPage(incident: ticket)));
        },
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(Icons.confirmation_number_outlined, size: 16, color: cs.onSurfaceVariant),
                      const SizedBox(width: 6),
                      Text(
                        ticket.ticketNumber,
                        style: TextStyle(color: cs.onSurfaceVariant, fontWeight: FontWeight.w600, fontSize: 13),
                      ),
                    ],
                  ),
                  StatusChip(status: ticket.status),
                ],
              ),
              const SizedBox(height: 14),
              Text(
                ticket.title,
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface, letterSpacing: -0.2),
              ),
              const SizedBox(height: 8),
              Text(
                ticket.description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontSize: 14, color: cs.onSurfaceVariant, height: 1.4),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
