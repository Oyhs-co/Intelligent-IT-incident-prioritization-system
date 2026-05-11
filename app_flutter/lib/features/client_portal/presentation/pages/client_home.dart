import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'new_report.dart';
import '../../models/providers/client_portal_providers.dart';
import 'incident_details.dart';
import '../../models/incident.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';

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
            : ListView.builder(
                physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                padding: const EdgeInsets.only(top: 8, bottom: 80),
                itemCount: listaDeTickets.length,
                itemBuilder: (context, index) {
                  return _ModernTicketCard(ticket: listaDeTickets[index]);
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
                  _buildStatusChip(ticket.status, cs),
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

  Widget _buildStatusChip(String status, ColorScheme cs) {
    Color bgColor;
    Color textColor;
    switch (status.toLowerCase()) {
      case 'resolved':
      case 'closed':
        bgColor = const Color(0xFFDEF7EC);
        textColor = const Color(0xFF03543F);
        break;
      case 'in_progress':
      case 'pending':
        bgColor = const Color(0xFFE1EFFE);
        textColor = const Color(0xFF1E429F);
        break;
      case 'open':
        bgColor = const Color(0xFFE0E7FF);
        textColor = const Color(0xFF4338CA);
        break;
      default:
        bgColor = const Color(0xFFFEF3C7);
        textColor = const Color(0xFF92400E);
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(20)),
      child: Text(
        _translateStatus(status),
        style: TextStyle(color: textColor, fontSize: 12, fontWeight: FontWeight.w700),
      ),
    );
  }

  String _translateStatus(String status) {
    switch (status.toLowerCase()) {
      case 'new': return 'Nuevo';
      case 'open': return 'Abierto';
      case 'in_progress': return 'En Progreso';
      case 'pending': return 'Pendiente';
      case 'resolved': return 'Resuelto';
      case 'closed': return 'Cerrado';
      default: return status;
    }
  }
}
