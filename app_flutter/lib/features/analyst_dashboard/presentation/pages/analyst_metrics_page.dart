import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/providers/analyst_dashboard_providers.dart';

class AnalystMetricsPage extends ConsumerStatefulWidget {
  const AnalystMetricsPage({super.key});

  @override
  ConsumerState<AnalystMetricsPage> createState() => _AnalystMetricsPageState();
}

class _AnalystMetricsPageState extends ConsumerState<AnalystMetricsPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(metricsOverviewProvider.notifier).fetchOverview();
      ref.read(metricsAIProvider.notifier).fetchAIMetrics();
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final overview = ref.watch(metricsOverviewProvider);
    final aiMetrics = ref.watch(metricsAIProvider);

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: const Text('Métricas del Sistema'),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await ref.read(metricsOverviewProvider.notifier).fetchOverview();
          await ref.read(metricsAIProvider.notifier).fetchAIMetrics();
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Incidentes', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Abiertos', '${overview?.incidentsOpen ?? 0}', Icons.inbox, const Color(0xFF2563EB), cs)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildStatCard('En Progreso', '${overview?.incidentsInProgress ?? 0}', Icons.autorenew, const Color(0xFFD97706), cs)),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Resueltos', '${overview?.incidentsResolved ?? 0}', Icons.check_circle, const Color(0xFF059669), cs)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildStatCard('Hoy', '${overview?.totalIncidentsToday ?? 0}', Icons.today, const Color(0xFF7C3AED), cs)),
                ],
              ),
              const SizedBox(height: 28),
              Text('Rendimiento', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Cumplimiento SLA', '${overview?.slaComplianceRate.toStringAsFixed(1) ?? "0"}%', Icons.shield, const Color(0xFF0D9488), cs)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildStatCard('Tiempo Prom. Res.', '${overview?.avgResolutionTimeMinutes.toStringAsFixed(0) ?? "0"} min', Icons.timer, const Color(0xFF475569), cs)),
                ],
              ),
              const SizedBox(height: 28),
              Text('Modelo de IA', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Confianza Prom.', '${(aiMetrics?.avgConfidence ?? 0 * 100).toStringAsFixed(0)}%', Icons.auto_awesome, const Color(0xFF4F46E5), cs)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildStatCard('Predicciones', '${aiMetrics?.totalPredictions ?? 0}', Icons.analytics, const Color(0xFF6D28D9), cs)),
                ],
              ),
              if (aiMetrics?.confidenceDistribution != null && aiMetrics!.confidenceDistribution.isNotEmpty) ...[
                const SizedBox(height: 28),
                Text('Distribución de Confianza', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: cs.onSurface)),
                const SizedBox(height: 16),
                _buildConfidenceBar('Alta (\u226580%)', aiMetrics.confidenceDistribution['high'] ?? 0, const Color(0xFF059669)),
                const SizedBox(height: 8),
                _buildConfidenceBar('Media (50-80%)', aiMetrics.confidenceDistribution['medium'] ?? 0, const Color(0xFFD97706)),
                const SizedBox(height: 8),
                _buildConfidenceBar('Baja (<50%)', aiMetrics.confidenceDistribution['low'] ?? 0, const Color(0xFFDC2626)),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color, ColorScheme cs) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(height: 14),
          Text(value, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w800, color: cs.onSurface)),
          const SizedBox(height: 4),
          Text(title, style: TextStyle(color: cs.onSurfaceVariant, fontWeight: FontWeight.w600, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildConfidenceBar(String label, int count, Color color) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
      ),
      child: Row(
        children: [
          Expanded(child: Text(label, style: TextStyle(fontWeight: FontWeight.w600, color: cs.onSurface))),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(20)),
            child: Text('$count', style: TextStyle(fontWeight: FontWeight.bold, color: color)),
          ),
        ],
      ),
    );
  }
}
