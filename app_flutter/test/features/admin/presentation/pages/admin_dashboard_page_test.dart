import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/admin/presentation/pages/admin_dashboard_page.dart';
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

void main() {
  testWidgets('AdminDashboardPage renders overview metrics', (
    WidgetTester tester,
  ) async {
    final overview = MetricsOverview(
      totalIncidentsToday: 2,
      totalIncidentsWeek: 6,
      totalIncidentsMonth: 20,
      incidentsOpen: 1,
      incidentsInProgress: 1,
      incidentsResolved: 4,
      incidentsClosed: 0,
      avgResponseTimeMinutes: 5,
      avgResolutionTimeMinutes: 30,
      slaComplianceRate: 90,
      slaBreachCount: 1,
      modelAccuracy: 0.9,
      modelConfidenceAvg: 0.8,
      aiPredictionsToday: 2,
      activeUsers: 4,
      activeTechnicians: 2,
    );

    await tester.pumpWidget(
      buildTestApp(
        const AdminDashboardPage(),
        overrides: [
          metricsOverviewProvider.overrideWith(
            () => TestMetricsOverviewNotifier(overview),
          ),
        ],
      ),
    );

    await tester.pump();

    expect(find.textContaining('Administración'), findsOneWidget);
    expect(find.text('Tickets Totales'), findsOneWidget);
    expect(find.text('Resueltos'), findsOneWidget);
  });
}
