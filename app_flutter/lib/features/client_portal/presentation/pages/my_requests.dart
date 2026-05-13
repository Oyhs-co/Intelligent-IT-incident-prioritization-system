import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../../../core/utils/app_translations.dart';
import '../../../auth/providers/auth_providers.dart';
import '../../../client_portal/models/providers/client_portal_providers.dart';
import '../../../client_portal/models/incident.dart';

class MyRequestsPage extends ConsumerStatefulWidget {
  const MyRequestsPage({super.key});

  @override
  ConsumerState<MyRequestsPage> createState() => _MyRequestsPageState();
}

class _MyRequestsPageState extends ConsumerState<MyRequestsPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabs;
  String _search = '';

  static const _tabStatuses = [
    'all',
    'in_progress',
    'resolved',
    'rejected',
  ];

  static const _tabLabels = [
    'Todos',
    'En Progreso',
    'Resueltos',
    'Rechazados',
  ];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: _tabStatuses.length, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(incidentProvider.notifier).fetchIncidents();
    });
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs          = Theme.of(context).colorScheme;
    final user        = ref.watch(authProvider).user;
    final allTickets  = ref.watch(incidentProvider);

    // Keep only MY tickets
    final mine = user == null
        ? allTickets
        : allTickets.where((t) => t.reporterId == user.id).toList();

    // Counts per tab
    final counts = _tabStatuses.map((s) {
      if (s == 'all') return mine.length;
      return mine.where((t) => t.status.toLowerCase() == s).length;
    }).toList();

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      drawer: const ModernSidebar(role: UserRole.client),
      appBar: AppBar(
        title: const Text('Mis Solicitudes'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(80),
          child: Column(
            children: [
              
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                child: TextField(
                  decoration: InputDecoration(
                    hintText: 'Buscar por ID o título…',
                    prefixIcon: Icon(Icons.search_outlined, size: 18, color: cs.onSurfaceVariant),
                    suffixIcon: _search.isNotEmpty
                        ? IconButton(
                            icon: Icon(Icons.close, size: 16, color: cs.onSurfaceVariant),
                            onPressed: () => setState(() => _search = ''),
                          )
                        : null,
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                  onChanged: (v) => setState(() => _search = v),
                ),
              ),
              
              TabBar(
                controller: _tabs,
                isScrollable: true,
                tabAlignment: TabAlignment.start,
                tabs: List.generate(_tabLabels.length, (i) => Tab(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_tabLabels[i]),
                      const SizedBox(width: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                        decoration: BoxDecoration(
                          color: cs.primaryContainer,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          '${counts[i]}',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: cs.primary),
                        ),
                      ),
                    ],
                  ),
                )),
              ),
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            tooltip: 'Actualizar',
            onPressed: () => ref.read(incidentProvider.notifier).fetchIncidents(),
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabs,
        children: List.generate(_tabStatuses.length, (i) {
          final tabStatus = _tabStatuses[i];
          final filtered  = mine.where((t) {
            final matchTab = tabStatus == 'all' || t.status.toLowerCase() == tabStatus;
            final matchSearch = _search.isEmpty ||
                t.title.toLowerCase().contains(_search.toLowerCase()) ||
                t.ticketNumber.toLowerCase().contains(_search.toLowerCase());
            return matchTab && matchSearch;
          }).toList();

          if (filtered.isEmpty) {
            return _EmptyState(tabLabel: _tabLabels[i]);
          }

          return RefreshIndicator(
            color: cs.primary,
            onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
            child: ListView.builder(
              physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
              itemCount: filtered.length,
              itemBuilder: (_, idx) => _RequestCard(ticket: filtered[idx]),
            ),
          );
        }),
      ),
    );
  }
}



class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.tabLabel});
  final String tabLabel;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.inbox_outlined, size: 64, color: cs.outlineVariant),
          const SizedBox(height: 14),
          Text(
            'Sin solicitudes en "$tabLabel"',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: cs.onSurface),
          ),
          const SizedBox(height: 6),
          Text(
            'Aquí aparecerán tus tickets cuando los crees.',
            style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13),
          ),
        ],
      ),
    );
  }
}

// ── Request card ───────────────────────────────────────────────────────────────

class _RequestCard extends StatelessWidget {
  const _RequestCard({required this.ticket});
  final Incident ticket;

  @override
  Widget build(BuildContext context) {
    final cs     = Theme.of(context).colorScheme;
    final sStyle = AppTranslations.statusStyle(ticket.status);
    final pStyle = AppTranslations.priorityStyle(ticket.finalPriority ?? ticket.priorityLabel);

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
              child: Container(width: 4, color: sStyle.accent),
            ),
            InkWell(
              onTap: () => context.pushNamed('incidentDetails', pathParameters: {'id': ticket.id}, extra: ticket),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      ticket.ticketNumber,
                      style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.w700),
                    ),
                  ),
                  // Status chip
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: sStyle.background,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      AppTranslations.status(ticket.status),
                      style: TextStyle(color: sStyle.text, fontSize: 10, fontWeight: FontWeight.w800),
                    ),
                  ),
                  if (ticket.finalPriority != null || ticket.priorityLabel != null) ...[
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: pStyle.background,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: pStyle.accent.withValues(alpha: 0.4)),
                      ),
                      child: Text(
                        AppTranslations.priority(ticket.finalPriority ?? ticket.priorityLabel),
                        style: TextStyle(color: pStyle.dark, fontSize: 10, fontWeight: FontWeight.w800),
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 10),
              Text(
                ticket.title,
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: cs.onSurface),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 6),
              Text(
                ticket.description,
                style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant, height: 1.4),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Icon(Icons.calendar_today_outlined, size: 12, color: cs.onSurfaceVariant),
                  const SizedBox(width: 4),
                  Text(
                    _fmt(ticket.createdAt),
                    style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant),
                  ),
                  if (ticket.category != null) ...[
                    const SizedBox(width: 12),
                    Icon(Icons.folder_outlined, size: 12, color: cs.onSurfaceVariant),
                    const SizedBox(width: 4),
                    Text(
                      AppTranslations.category(ticket.category),
                      style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant),
                    ),
                  ],
                  const Spacer(),
                  Icon(Icons.chevron_right, size: 16, color: cs.primary),
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

  String _fmt(String d) {
    try {
      final dt = DateTime.parse(d);
      const m = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
      return '${dt.day} ${m[dt.month - 1]} ${dt.year}';
    } catch (_) {
      return d;
    }
  }
}
