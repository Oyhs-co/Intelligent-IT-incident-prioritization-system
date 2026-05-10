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
    final overview = ref.watch(metricsOverviewProvider);
    final aiMetrics = ref.watch(metricsAIProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text('Métricas del Sistema', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800)),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await ref.read(metricsOverviewProvider.notifier).fetchOverview();
          await ref.read(metricsAIProvider.notifier).fetchAIMetrics();
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Incidentes', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Abiertos', '${overview?.incidentsOpen ?? 0}', Icons.inbox, Colors.blue)),
                  const SizedBox(width: 16),
                  Expanded(child: _buildStatCard('En Progreso', '${overview?.incidentsInProgress ?? 0}', Icons.autorenew, Colors.orange)),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Resueltos', '${overview?.incidentsResolved ?? 0}', Icons.check_circle, Colors.green)),
                  const SizedBox(width: 16),
                  Expanded(child: _buildStatCard('Hoy', '${overview?.totalIncidentsToday ?? 0}', Icons.today, Colors.purple)),
                ],
              ),
              const SizedBox(height: 32),
              const Text('Rendimiento', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Cumplimiento SLA', '${overview?.slaComplianceRate.toStringAsFixed(1) ?? "0"}%', Icons.shield, Colors.teal)),
                  const SizedBox(width: 16),
                  Expanded(child: _buildStatCard('Tiempo Prom. Res.', '${overview?.avgResolutionTimeMinutes.toStringAsFixed(0) ?? "0"} min', Icons.timer, Colors.blueGrey)),
                ],
              ),
              const SizedBox(height: 32),
              const Text('Modelo de IA', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(child: _buildStatCard('Confianza Prom.', '${(aiMetrics?.avgConfidence ?? 0 * 100).toStringAsFixed(0)}%', Icons.auto_awesome, Colors.indigo)),
                  const SizedBox(width: 16),
                  Expanded(child: _buildStatCard('Predicciones', '${aiMetrics?.totalPredictions ?? 0}', Icons.analytics, Colors.deepPurple)),
                ],
              ),
              if (aiMetrics?.confidenceDistribution != null && aiMetrics!.confidenceDistribution.isNotEmpty) ...[
                const SizedBox(height: 32),
                const Text('Distribución de Confianza', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                _buildConfidenceBar('Alta (\u226580%)', aiMetrics.confidenceDistribution['high'] ?? 0, Colors.green),
                const SizedBox(height: 8),
                _buildConfidenceBar('Media (50-80%)', aiMetrics.confidenceDistribution['medium'] ?? 0, Colors.orange),
                const SizedBox(height: 8),
                _buildConfidenceBar('Baja (<50%)', aiMetrics.confidenceDistribution['low'] ?? 0, Colors.red),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(12)),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 16),
          Text(value, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800)),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildConfidenceBar(String label, int count, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
      ),
      child: Row(
        children: [
          Expanded(child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600))),
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
