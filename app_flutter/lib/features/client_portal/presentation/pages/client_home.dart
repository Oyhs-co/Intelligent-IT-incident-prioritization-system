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
    final todosLosTickets = ref.watch(incidentProvider);
    final filtroActual = ref.watch(clientFilterProvider);

    final listaDeTickets = filtroActual == 'Todos'
        ? todosLosTickets
        : todosLosTickets.where((t) => _matchFilter(t.status, filtroActual)).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      drawer: const ModernSidebar(),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        title: Text(
          'mis incidentes${filtroActual != "Todos" ? " ($filtroActual)" : ""}',
          style: const TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 22, letterSpacing: -0.5),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
        child: listaDeTickets.isEmpty
            ? const Center(
                child: Text('no tienes incidentes reportados.', style: TextStyle(color: Colors.black54)),
              )
            : ListView.builder(
                physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                padding: const EdgeInsets.only(top: 8, bottom: 80),
                itemCount: listaDeTickets.length,
                itemBuilder: (context, index) {
                  final ticketActual = listaDeTickets[index];
                  return _ModernTicketCard(ticket: ticketActual);
                },
              ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(context, MaterialPageRoute(builder: (context) => const NewReportPage()));
        },
        elevation: 2,
        backgroundColor: const Color(0xFF0F172A),
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_rounded, size: 20),
        label: const Text('nuevo reporte', style: TextStyle(fontWeight: FontWeight.w600, letterSpacing: 0.2)),
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
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 12, offset: const Offset(0, 6)),
        ],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => IncidentDetailsPage(incident: ticket)),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.confirmation_number_outlined, size: 16, color: Colors.black45),
                      const SizedBox(width: 6),
                      Text(
                        ticket.ticketNumber,
                        style: const TextStyle(color: Colors.black54, fontWeight: FontWeight.w600, fontSize: 13, letterSpacing: 0.5),
                      ),
                    ],
                  ),
                  _buildStatusChip(ticket.status),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                ticket.title,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF111827), letterSpacing: -0.3),
              ),
              const SizedBox(height: 8),
              Text(
                ticket.description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 14, color: Color(0xFF6B7280), height: 1.5),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
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
      case 'new': return 'nuevo';
      case 'open': return 'abierto';
      case 'in_progress': return 'en progreso';
      case 'pending': return 'pendiente';
      case 'resolved': return 'resuelto';
      case 'closed': return 'cerrado';
      default: return status;
    }
  }
}
