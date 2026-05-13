import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import '../../../analyst_dashboard/models/providers/analyst_dashboard_providers.dart';

class AdminDashboardPage extends ConsumerStatefulWidget {
  const AdminDashboardPage({super.key});

  @override
  ConsumerState<AdminDashboardPage> createState() => _AdminDashboardPageState();
}

class _AdminDashboardPageState extends ConsumerState<AdminDashboardPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(metricsOverviewProvider.notifier).fetchOverview();
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final overview = ref.watch(metricsOverviewProvider);

    final totalTickets = (overview?.incidentsOpen ?? 0) + (overview?.incidentsInProgress ?? 0) + (overview?.incidentsResolved ?? 0);
    final resueltos = overview?.incidentsResolved ?? 0;
    final enProgreso = overview?.incidentsInProgress ?? 0;
    final criticos = overview?.totalIncidentsToday ?? 0;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      drawer: const ModernSidebar(role: UserRole.admin),
      appBar: AppBar(
        title: const Text('Administración'),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(metricsOverviewProvider.notifier).fetchOverview(),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Visión General', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(child: _buildMetricCard('Tickets Totales', '$totalTickets', Icons.receipt_long, cs.primary, cs)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildMetricCard('Resueltos', '$resueltos', Icons.check_circle_outline, const Color(0xFF059669), cs)),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _buildMetricCard('En Progreso', '$enProgreso', Icons.autorenew, const Color(0xFFD97706), cs)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildMetricCard('Incidentes Hoy', '$criticos', Icons.warning_amber_rounded, const Color(0xFFDC2626), cs)),
                ],
              ),
              const SizedBox(height: 32),
              Text('Módulos Administrativos', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
              const SizedBox(height: 16),
              _buildAdminModule(
                cs: cs,
                title: 'Control Global de Tickets',
                subtitle: 'Monitorear todos los tickets del sistema.',
                icon: Icons.confirmation_number_outlined,
                color: cs.primary,
                routeName: 'adminTickets',
              ),
              _buildAdminModule(
                cs: cs,
                title: 'Gestión de Usuarios y Roles',
                subtitle: 'Crear, editar o suspender cuentas.',
                icon: Icons.people_alt_outlined,
                color: const Color(0xFF059669),
                routeName: 'adminUsers',
              ),
              _buildAdminModule(
                cs: cs,
                title: 'Ajustes del Modelo de IA',
                subtitle: 'Configurar parámetros de auto-asignación y prioridad.',
                icon: Icons.auto_awesome,
                color: const Color(0xFF7C3AED),
                routeName: 'adminAISettings',
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color, ColorScheme cs) {
    return Container(
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, size: 24, color: color),
          ),
          const SizedBox(height: 14),
          Text(value, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w800, color: cs.onSurface)),
          const SizedBox(height: 4),
          Text(title, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: cs.onSurfaceVariant)),
        ],
      ),
    );
  }

  Widget _buildAdminModule({
    required ColorScheme cs,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required String routeName,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: () => context.pushNamed(routeName),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: color.withValues(alpha: 0.1), shape: BoxShape.circle),
                  child: Icon(icon, color: color, size: 24),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: cs.onSurface)),
                      const SizedBox(height: 4),
                      Text(subtitle, style: TextStyle(fontSize: 13, color: cs.onSurfaceVariant, height: 1.3)),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Icon(Icons.arrow_forward_ios, size: 16, color: cs.onSurfaceVariant),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
