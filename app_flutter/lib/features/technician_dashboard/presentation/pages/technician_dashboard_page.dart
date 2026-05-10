import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../../client_portal/models/incident.dart';
import '../../../client_portal/models/providers/client_portal_providers.dart';
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
    final tickets = ref.watch(incidentProvider);
    final ticketsPendientes = tickets.where((t) => t.status == 'in_progress').toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      drawer: const ModernSidebar(role: UserRole.technician),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text(
          'Bandeja del Técnico',
          style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18, letterSpacing: -0.5),
        ),
      ),
      body: ticketsPendientes.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle_outline, size: 64, color: Colors.green),
                  SizedBox(height: 16),
                  Text('¡Excelente trabajo!', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF111827))),
                  SizedBox(height: 8),
                  Text('No tienes tickets pendientes en tu área.', style: TextStyle(color: Colors.grey)),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: () => ref.read(incidentProvider.notifier).fetchIncidents(),
              child: ListView.builder(
                padding: const EdgeInsets.all(24),
                itemCount: ticketsPendientes.length,
                itemBuilder: (context, index) {
                  final ticket = ticketsPendientes[index];
                  return _TechnicianTicketCard(ticket: ticket);
                },
              ),
            ),
    );
  }
}

class _TechnicianTicketCard extends StatelessWidget {
  final Incident ticket;
  const _TechnicianTicketCard({required this.ticket});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.05)),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => TechnicianResolvePage(ticket: ticket)),
          );
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
                    ticket.id,
                    style: const TextStyle(color: Colors.black54, fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF2F2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Prioridad ${ticket.finalPriority ?? ticket.priorityLabel ?? "Media"}',
                      style: const TextStyle(color: Color(0xFFDC2626), fontWeight: FontWeight.bold, fontSize: 11),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                ticket.title,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827)),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.build_circle, size: 16, color: Color(0xFF2563EB)),
                  const SizedBox(width: 6),
                  Text(
                    ticket.category ?? 'Área no asignada',
                    style: const TextStyle(color: Color(0xFF2563EB), fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
