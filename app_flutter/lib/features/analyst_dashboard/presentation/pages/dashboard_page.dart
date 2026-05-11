import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';
import '../../../../features/client_portal/models/incident.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../models/providers/analyst_providers.dart';
import 'incident_review_page.dart';

class AnalystDashboardPage extends ConsumerStatefulWidget {
  const AnalystDashboardPage({super.key});
  @override
  ConsumerState<AnalystDashboardPage> createState() => _AnalystDashboardPageState();
}

class _AnalystDashboardPageState extends ConsumerState<AnalystDashboardPage> {
  String filtroBusqueda = '';

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
    final listaCompleta = ref.watch(incidentProvider);
    final filtroGlobal = ref.watch(analystFilterProvider);

    final listaFiltrada = listaCompleta.where((ticket) {
      final tituloCoincide = ticket.title.toLowerCase().contains(filtroBusqueda.toLowerCase());
      final idCoincide = ticket.ticketNumber.toLowerCase().contains(filtroBusqueda.toLowerCase());
      final prioridadCoincide = filtroGlobal == 'Todas' || _matchPriority(ticket, filtroGlobal);
      return (tituloCoincide || idCoincide) && prioridadCoincide;
    }).toList();

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      drawer: const ModernSidebar(role: UserRole.analyst),
      appBar: AppBar(
        title: Text(
          'Incidentes${filtroGlobal != "Todas" ? " ($filtroGlobal)" : ""}',
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 20),
            TextField(
              decoration: InputDecoration(
                hintText: 'Buscar por ID o título...',
                prefixIcon: Icon(Icons.search, color: cs.onSurfaceVariant),
                fillColor: cs.surface,
              ),
              onChanged: (valor) => setState(() => filtroBusqueda = valor),
            ),
            const SizedBox(height: 20),
            Text(
              'Resultados (${listaFiltrada.length})',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: cs.onSurfaceVariant),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: listaFiltrada.isEmpty
                  ? Center(child: Text('No hay incidentes.', style: TextStyle(color: cs.onSurfaceVariant)))
                  : RefreshIndicator(
                      onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
                      child: ListView.builder(
                        physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                        itemCount: listaFiltrada.length,
                        itemBuilder: (context, index) {
                          return _AnalystTicketCard(ticket: listaFiltrada[index]);
                        },
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  bool _matchPriority(Incident ticket, String filter) {
    final label = (ticket.finalPriority ?? ticket.priorityLabel ?? '').toLowerCase();
    switch (filter.toLowerCase()) {
      case 'crítica':
        return label == 'crítica' || label == 'critica' || label == 'critical' || label == 'p4 (critical)';
      case 'alta':
        return label == 'alta' || label == 'high' || label == 'p3 (high)';
      case 'media':
        return label == 'media' || label == 'medium' || label == 'p2 (medium)';
      case 'baja':
        return label == 'baja' || label == 'low' || label == 'p1 (low)';
      default:
        return true;
    }
  }
}

class _AnalystTicketCard extends StatelessWidget {
  final Incident ticket;
  const _AnalystTicketCard({required this.ticket});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => IncidentReviewPage(ticket: ticket))),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(ticket.ticketNumber, style: TextStyle(color: cs.onSurfaceVariant, fontWeight: FontWeight.w600, fontSize: 13)),
                  _buildPriorityChip(ticket.finalPriority ?? ticket.priorityLabel ?? ''),
                ],
              ),
              const SizedBox(height: 12),
              Text(ticket.title, style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface, letterSpacing: -0.2)),
              const SizedBox(height: 8),
              Text(ticket.description, maxLines: 2, overflow: TextOverflow.ellipsis,
                style: TextStyle(fontSize: 14, color: cs.onSurfaceVariant, height: 1.4)),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 14),
                child: Divider(height: 1, color: cs.outlineVariant.withValues(alpha: 0.5)),
              ),
              Row(
                children: [
                  Icon(Icons.auto_awesome, size: 16, color: cs.primary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'IA: ${ticket.priorityLabel ?? "Sin clasificar"} '
                      '${ticket.confidenceScore != null ? "(${(ticket.confidenceScore! * 100).toInt()}%)" : ""}',
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.primary),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPriorityChip(String label) {
    Color bgColor;
    Color textColor;
    switch (label.toLowerCase()) {
      case 'crítica':
      case 'critica':
      case 'critical':
      case 'p4 (critical)':
        bgColor = const Color(0xFF7F1D1D);
        textColor = Colors.white;
        break;
      case 'alta':
      case 'high':
      case 'p3 (high)':
        bgColor = const Color(0xFFFEE2E2);
        textColor = const Color(0xFF991B1B);
        break;
      case 'media':
      case 'medium':
      case 'p2 (medium)':
        bgColor = const Color(0xFFFEF3C7);
        textColor = const Color(0xFF92400E);
        break;
      default:
        bgColor = const Color(0xFFDEF7EC);
        textColor = const Color(0xFF03543F);
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(20)),
      child: Text(label.toUpperCase(), style: TextStyle(color: textColor, fontSize: 11, fontWeight: FontWeight.w800)),
    );
  }
}
