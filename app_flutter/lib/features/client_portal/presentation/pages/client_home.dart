import 'package:flutter/material.dart';
import 'new_report.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/providers/client_portal_providers.dart';

class ClientHome extends ConsumerWidget {
  const ClientHome({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Lista de tickets desde el estado.
    final listaDeTickets = ref.watch(incidentProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Mis Solicitudes')),

      body: ListView.builder(
        itemCount: listaDeTickets.length,

        itemBuilder: (context, index) {
          final ticketActual = listaDeTickets[index];

          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ListTile(
              leading: const CircleAvatar(
                backgroundColor: Colors.blueAccent,
                child: Icon(Icons.computer, color: Colors.white),
              ),

              title: Text('${ticketActual.id}: ${ticketActual.title}'),
              subtitle: Text('Estado: ${ticketActual.status}'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Navega al formulario para crear un nuevo reporte.
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => NewReportPage()),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
