import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';

class AnalystHistoryPage extends ConsumerWidget {
  const AnalystHistoryPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tickets = ref.watch(incidentProvider);
    final resueltos = tickets.where((t) => t.status.toLowerCase() == 'resuelto').toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text('Historial de Resueltos', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800)),
      ),
      body: resueltos.isEmpty
          ? const Center(child: Text('No hay tickets resueltos en tu historial.', style: TextStyle(color: Colors.black54)))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: resueltos.length,
              itemBuilder: (context, index) {
                final ticket = resueltos[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(color: Colors.black.withValues(alpha: 0.08)),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    leading: const CircleAvatar(
                      backgroundColor: Color(0xFFDEF7EC),
                      child: Icon(Icons.check_circle, color: Color(0xFF03543F)),
                    ),
                    title: Text('${ticket.id}: ${ticket.title}', style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('Resolución: ${ticket.finalResolution ?? "Sin detalles"}'),
                    trailing: Text(ticket.aiPriority, style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                  ),
                );
              },
            ),
    );
  }
}
