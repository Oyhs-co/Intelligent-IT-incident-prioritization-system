import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/presentation/pages/analyst_directory_page.dart';
import '../../../../helpers/test_app.dart';

void main() {
  testWidgets('AnalystDirectoryPage shows loading indicator first', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(buildTestApp(const AnalystDirectoryPage()));

    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
