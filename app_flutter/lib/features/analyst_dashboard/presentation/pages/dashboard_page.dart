import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';
import '../../../../features/client_portal/models/incident.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../../../core/utils/app_translations.dart';
import '../../models/providers/analyst_providers.dart';
import 'incident_review_page.dart';

class AnalystDashboardPage extends ConsumerStatefulWidget {
  const AnalystDashboardPage({super.key});
  @override
  ConsumerState<AnalystDashboardPage> createState() => _AnalystDashboardPageState();
}

class _AnalystDashboardPageState extends ConsumerState<AnalystDashboardPage> {
  String _search = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(incidentProvider.notifier).fetchIncidents();
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs           = Theme.of(context).colorScheme;
    final all          = ref.watch(incidentProvider);
    final priorityFilter = ref.watch(analystFilterProvider);

    final filtered = all.where((t) {
      final matchSearch = t.title.toLowerCase().contains(_search.toLowerCase()) ||
          t.ticketNumber.toLowerCase().contains(_search.toLowerCase());
      final matchPriority = priorityFilter == 'Todas' || _matchPriority(t, priorityFilter);
      return matchSearch && matchPriority;
    }).toList();

    // KPI counts
    final critica = all.where((t) => _isPriority(t, 'Crítica')).length;
    final alta    = all.where((t) => _isPriority(t, 'Alta')).length;
    final media   = all.where((t) => _isPriority(t, 'Media')).length;
    final baja    = all.where((t) => _isPriority(t, 'Baja')).length;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      drawer: const ModernSidebar(role: UserRole.analyst),
      appBar: AppBar(
        title: const Text('Centro de Incidentes'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            tooltip: 'Actualizar',
            onPressed: () => ref.read(incidentProvider.notifier).fetchIncidents(),
          ),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
         
          Container(
            color: cs.surface,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: [
                _KpiPill('Crítica', critica, const Color(0xFF991B1B)),
                const SizedBox(width: 6),
                _KpiPill('Alta',    alta,    const Color(0xFFDC2626)),
                const SizedBox(width: 6),
                _KpiPill('Media',   media,   const Color(0xFFD97706)),
                const SizedBox(width: 6),
                _KpiPill('Baja',    baja,    const Color(0xFF059669)),
                const Spacer(),
                Text(
                  '${all.length} total',
                  style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant, fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
          const Divider(height: 1),

         
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 6),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Buscar por ID o título…',
                prefixIcon: Icon(Icons.search_outlined, size: 20, color: cs.onSurfaceVariant),
                suffixIcon: _search.isNotEmpty
                    ? IconButton(
                        icon: Icon(Icons.close, size: 18, color: cs.onSurfaceVariant),
                        onPressed: () => setState(() => _search = ''),
                      )
                    : null,
              ),
              onChanged: (v) => setState(() => _search = v),
            ),
          ),

          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            child: Text(
              '${filtered.length} resultado${filtered.length != 1 ? "s" : ""}',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant),
            ),
          ),

          
          Expanded(
            child: filtered.isEmpty
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.inbox_outlined, size: 56, color: cs.outlineVariant),
                        const SizedBox(height: 12),
                        Text('Sin incidentes', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 15)),
                      ],
                    ),
                  )
                : RefreshIndicator(
                    color: cs.primary,
                    onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
                    child: _ResponsiveList(tickets: filtered),
                  ),
          ),
        ],
      ),
    );
  }

  bool _matchPriority(Incident t, String filter) {
    final label = AppTranslations.priority(t.finalPriority ?? t.priorityLabel ?? '');
    return label.toLowerCase() == filter.toLowerCase();
  }

  bool _isPriority(Incident t, String p) => _matchPriority(t, p);
}



class _ResponsiveList extends StatelessWidget {
  const _ResponsiveList({required this.tickets});
  final List<Incident> tickets;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;

    if (w >= 1100) {
      return GridView.builder(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 1.55,
        ),
        itemCount: tickets.length,
        itemBuilder: (_, i) => _AnalystTicketCard(ticket: tickets[i]),
      );
    }
    if (w >= 700) {
      return GridView.builder(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 1.55,
        ),
        itemCount: tickets.length,
        itemBuilder: (_, i) => _AnalystTicketCard(ticket: tickets[i]),
      );
    }
    return ListView.builder(
      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      itemCount: tickets.length,
      itemBuilder: (_, i) => _AnalystTicketCard(ticket: tickets[i]),
    );
  }
}



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


class _AnalystTicketCard extends StatelessWidget {
  final Incident ticket;
  const _AnalystTicketCard({required this.ticket});

  static Color _pColor(String? raw) =>
      AppTranslations.priorityStyle(raw).accent;

  @override
  Widget build(BuildContext context) {
    final cs    = Theme.of(context).colorScheme;
    final pRaw  = ticket.finalPriority ?? ticket.priorityLabel ?? '';
    final color = _pColor(pRaw);
    final pLabel = AppTranslations.priority(pRaw);

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.5)),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => IncidentReviewPage(ticket: ticket)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    ticket.ticketNumber,
                    style: TextStyle(
                      color: cs.onSurfaceVariant,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: color.withValues(alpha: 0.4)),
                    ),
                    child: Text(
                      pLabel.toUpperCase(),
                      style: TextStyle(
                        color: color,
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),

              
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 3,
                    height: 36,
                    margin: const EdgeInsets.only(right: 10),
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  Expanded(
                    child: Text(
                      ticket.title,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: cs.onSurface,
                        letterSpacing: -0.2,
                        height: 1.3,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              
              Text(
                ticket.description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12,
                  color: cs.onSurfaceVariant,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 10),

              
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: cs.primaryContainer.withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.psychology_outlined, size: 12, color: cs.primary),
                    const SizedBox(width: 4),
                    Flexible(
                      child: Text(
                        'IA: ${AppTranslations.priority(ticket.priorityLabel)}'
                        '${ticket.confidenceScore != null ? " · ${(ticket.confidenceScore! * 100).toInt()}%" : ""}',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: cs.primary,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
