import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/client_portal/models/incident.dart';

void main() {
  test('Incident.fromJson parses required fields', () {
    final json = {
      'id': '1',
      'ticket_number': 'T-100',
      'title': 'Printer error',
      'description': 'Paper jam',
      'status': 'open',
      'created_at': '2026-05-01T08:00:00Z',
      'updated_at': '2026-05-01T08:00:00Z',
    };

    final incident = Incident.fromJson(json);

    expect(incident.id, '1');
    expect(incident.ticketNumber, 'T-100');
    expect(incident.title, 'Printer error');
    expect(incident.description, 'Paper jam');
    expect(incident.status, 'open');
    expect(incident.urgency, 3);
    expect(incident.impact, 3);
  });

  test('Incident.copyWith overrides fields', () {
    final incident = Incident(
      id: '1',
      ticketNumber: 'T-100',
      title: 'Printer error',
      description: 'Paper jam',
      status: 'open',
      createdAt: '2026-05-01T08:00:00Z',
      updatedAt: '2026-05-01T08:00:00Z',
    );

    final updated = incident.copyWith(status: 'resolved', priority: 3);

    expect(updated.status, 'resolved');
    expect(updated.priority, 3);
    expect(updated.ticketNumber, 'T-100');
  });
}
