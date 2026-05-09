import 'package:flutter/material.dart';
import 'new_report.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/providers/client_portal_providers.dart';
import 'incident_details.dart';
import '../../../auth/presentation/pages/login_page.dart';

class ClientHome extends ConsumerWidget {
  const ClientHome({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final listaDeTickets = ref.watch(incidentProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Solicitudes'),
        actions: [
          IconButton(
            tooltip: 'Cerrar sesion',
            icon: const Icon(Icons.logout),
            onPressed: () {
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (context) => const LoginPage()),
                (route) => false,
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          // Aquí simulamos una espera de 1.5 segundos para que veas el círculo de carga.
          // En el futuro, aquí llamarías a tu API para descargar nuevos datos.
          await Future.delayed(const Duration(milliseconds: 1500));
        },
        child: ListView.builder(
          physics: const AlwaysScrollableScrollPhysics(),
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
                subtitle: Text(
                  ticketActual.description,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) =>
                          IncidentDetailsPage(incident: ticketActual),
                    ),
                  );
                },
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
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
