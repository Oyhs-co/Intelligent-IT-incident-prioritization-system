import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/presentation/pages/analyst_metrics_page.dart';
import 'package:app_flutter/features/analyst_dashboard/models/dashboard_metrics.dart';
import 'package:app_flutter/features/analyst_dashboard/models/providers/analyst_dashboard_providers.dart';
import '../../../../helpers/test_app.dart';

class TestMetricsOverviewNotifier extends MetricsOverviewNotifier {
  TestMetricsOverviewNotifier(this._value);
  final MetricsOverview _value;

  @override
  MetricsOverview? build() => _value;

  @override
  Future<void> fetchOverview() async {}
}

class TestMetricsAINotifier extends MetricsAINotifier {
  TestMetricsAINotifier(this._value);
  final MetricsAI _value;

  @override
  MetricsAI? build() => _value;

  @override
  Future<void> fetchAIMetrics() async {}
}

void main() {
  testWidgets('AnalystMetricsPage renders stats', (WidgetTester tester) async {
    final overview = MetricsOverview(
      totalIncidentsToday: 4,
      totalIncidentsWeek: 10,
      totalIncidentsMonth: 20,
      incidentsOpen: 1,
      incidentsInProgress: 2,
      incidentsResolved: 3,
      incidentsClosed: 0,
      avgResponseTimeMinutes: 10,
      avgResolutionTimeMinutes: 50,
      slaComplianceRate: 95,
      slaBreachCount: 1,
      modelAccuracy: 0.9,
      modelConfidenceAvg: 0.75,
      aiPredictionsToday: 6,
      activeUsers: 2,
      activeTechnicians: 1,
    );

    final ai = MetricsAI(
      totalPredictions: 12,
      accuracy: 0.85,
      avgConfidence: 0.7,
      confidenceDistribution: const {'high': 4},
    );

    await tester.pumpWidget(
      buildTestApp(
        const AnalystMetricsPage(),
        overrides: [
          metricsOverviewProvider.overrideWith(
            () => TestMetricsOverviewNotifier(overview),
          ),
          metricsAIProvider.overrideWith(() => TestMetricsAINotifier(ai)),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('Métricas del Sistema'), findsOneWidget);
    expect(find.text('Resueltos'), findsOneWidget);
    expect(find.text('Predicciones'), findsOneWidget);
  });
}
