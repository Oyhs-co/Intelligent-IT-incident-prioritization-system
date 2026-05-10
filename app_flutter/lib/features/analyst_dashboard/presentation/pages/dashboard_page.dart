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
    final listaCompleta = ref.watch(incidentProvider);
    final filtroGlobal = ref.watch(analystFilterProvider);

    final listaFiltrada = listaCompleta.where((ticket) {
      final tituloCoincide = ticket.title.toLowerCase().contains(filtroBusqueda.toLowerCase());
      final idCoincide = ticket.ticketNumber.toLowerCase().contains(filtroBusqueda.toLowerCase());
      final prioridadCoincide = filtroGlobal == 'Todas' || _matchPriority(ticket, filtroGlobal);
      return (tituloCoincide || idCoincide) && prioridadCoincide;
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      drawer: const ModernSidebar(role: UserRole.analyst),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text(
          'Triage de Incidentes${filtroGlobal != "Todas" ? " ($filtroGlobal)" : ""}',
          style: const TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 22, letterSpacing: -0.5),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 24),
            TextField(
              decoration: InputDecoration(
                hintText: 'Buscar por ID o título...',
                prefixIcon: const Icon(Icons.search, color: Color(0xFF6B7280)),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
                filled: true,
                fillColor: Colors.white,
                contentPadding: const EdgeInsets.symmetric(vertical: 16),
              ),
              onChanged: (valor) => setState(() => filtroBusqueda = valor),
            ),
            const SizedBox(height: 24),
            Text(
              'Bandeja de Entrada (${listaFiltrada.length})',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF6B7280)),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: listaFiltrada.isEmpty
                  ? const Center(child: Text('No hay incidentes.', style: TextStyle(color: Colors.black54)))
                  : RefreshIndicator(
                      onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
                      child: ListView.builder(
                        physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                        itemCount: listaFiltrada.length,
                        itemBuilder: (context, index) {
                          final ticket = listaFiltrada[index];
                          return _AnalystTicketCard(ticket: ticket);
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
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 12, offset: const Offset(0, 6))],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => IncidentReviewPage(ticket: ticket))),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(ticket.ticketNumber, style: const TextStyle(color: Colors.black54, fontWeight: FontWeight.w600, fontSize: 13, letterSpacing: 0.5)),
                  _buildPriorityChip(ticket.finalPriority ?? ticket.priorityLabel ?? ''),
                ],
              ),
              const SizedBox(height: 12),
              Text(ticket.title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF111827), letterSpacing: -0.3)),
              const SizedBox(height: 8),
              Text(ticket.description, maxLines: 2, overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 14, color: Color(0xFF6B7280), height: 1.5)),
              const Padding(padding: EdgeInsets.symmetric(vertical: 16.0), child: Divider(height: 1, color: Color(0xFFF3F4F6))),
                  Row(
                    children: [
                      const Icon(Icons.auto_awesome, size: 16, color: Color(0xFF2563EB)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'IA: ${ticket.priorityLabel ?? "Sin clasificar"} '
                          '${ticket.confidenceScore != null ? "(${(ticket.confidenceScore! * 100).toInt()}%)" : ""}',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF2563EB)),
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
