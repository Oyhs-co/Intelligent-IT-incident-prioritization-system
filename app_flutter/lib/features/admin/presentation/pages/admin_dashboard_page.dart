import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/presentation/widgets/modern_sidebar.dart';
import 'global_tickets_page.dart';
import 'user_management_page.dart';
import 'ai_settings_page.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';

class AdminDashboardPage extends ConsumerWidget {
  const AdminDashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tickets = ref.watch(incidentProvider);
    
    final totalTickets = tickets.length;
    final resueltos = tickets.where((t) => t.status.toLowerCase() == 'resuelto').length;
    final enProgreso = tickets.where((t) => t.status.toLowerCase() == 'en progreso' || t.status.toLowerCase() == 'enviando...').length;
    final criticos = tickets.where((t) => t.aiPriority == 'Alta' && t.status.toLowerCase() != 'resuelto').length;
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      drawer: const ModernSidebar(role: UserRole.admin),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text(
          'Administración',
          style: TextStyle(
            color: Color(0xFF111827),
            fontWeight: FontWeight.w800,
            fontSize: 22,
            letterSpacing: -0.5,
          ),
        ),
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Visión General',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827)),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: _buildMetricCard('Tickets Totales', '$totalTickets', Icons.receipt_long, const Color(0xFF2563EB))),
                const SizedBox(width: 16),
                Expanded(child: _buildMetricCard('Resueltos', '$resueltos', Icons.check_circle_outline, const Color(0xFF059669))),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: _buildMetricCard('En Progreso', '$enProgreso', Icons.autorenew, const Color(0xFFD97706))),
                const SizedBox(width: 16),
                Expanded(child: _buildMetricCard('Alertas Críticas', '$criticos', Icons.warning_amber_rounded, const Color(0xFFDC2626))),
              ],
            ),
            const SizedBox(height: 32),
            const Text(
              'Módulos Administrativos',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827)),
            ),
            const SizedBox(height: 16),
            _buildAdminModule(
              context: context,
              title: 'Control Global de Tickets',
              subtitle: 'Monitorear todos los tickets del sistema independientemente del área.',
              icon: Icons.confirmation_number_outlined,
              color: const Color(0xFF2563EB),
              destination: const GlobalTicketsPage(),
            ),
            _buildAdminModule(
              context: context,
              title: 'Gestión de Usuarios y Roles',
              subtitle: 'Crear, editar o suspender cuentas de clientes, analistas y técnicos.',
              icon: Icons.people_alt_outlined,
              color: const Color(0xFF059669),
              destination: const UserManagementPage(),
            ),
            _buildAdminModule(
              context: context,
              title: 'Ajustes del Modelo de IA',
              subtitle: 'Configurar parámetros de auto-asignación y niveles de prioridad.',
              icon: Icons.auto_awesome,
              color: const Color(0xFF7C3AED),
              destination: const AISettingsPage(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, size: 24, color: color),
          ),
          const SizedBox(height: 16),
          Text(
            value,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: Color(0xFF111827)),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF6B7280)),
          ),
        ],
      ),
    );
  }

  Widget _buildAdminModule({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required Widget destination,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 4)),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            Navigator.push(context, MaterialPageRoute(builder: (context) => destination));
          },
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: color, size: 24),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: Color(0xFF111827))),
                      const SizedBox(height: 4),
                      Text(subtitle, style: const TextStyle(fontSize: 13, color: Color(0xFF6B7280), height: 1.4)),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                const Icon(Icons.arrow_forward_ios, size: 16, color: Color(0xFF9CA3AF)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
