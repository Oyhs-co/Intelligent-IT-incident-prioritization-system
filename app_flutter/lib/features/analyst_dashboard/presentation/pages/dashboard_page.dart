import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';
import '../../../auth/presentation/pages/login_page.dart';

class AnalystDashboardPage extends ConsumerStatefulWidget {
  const AnalystDashboardPage({super.key});
  @override
  ConsumerState<AnalystDashboardPage> createState() =>
      _AnalystDashboardPageState();
}

class _AnalystDashboardPageState extends ConsumerState<AnalystDashboardPage> {
  String filtroBusqueda = '';
  @override
  Widget build(BuildContext context) {
    final listaCompleta = ref.watch(incidentProvider);
    final listaFiltrada = listaCompleta.where((ticket) {
      final tituloCoincide = ticket.title.toLowerCase().contains(
        filtroBusqueda.toLowerCase(),
      );
      final idCoincide = ticket.id.toLowerCase().contains(
        filtroBusqueda.toLowerCase(),
      );
      return tituloCoincide || idCoincide;
    }).toList();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Panel de Analista IT - SIPIIT'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
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
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Bandeja de Entrada',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                ),
                Chip(label: Text('${listaFiltrada.length} Resultados')),
              ],
            ),
            const SizedBox(height: 15),
            TextField(
              decoration: InputDecoration(
                hintText: 'Buscar por ID o palabra clave...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
                filled: true,
                fillColor: Colors.grey[100],
              ),
              onChanged: (valor) {
                setState(() {
                  filtroBusqueda = valor;
                });
              },
            ),
            const SizedBox(height: 15),
            Expanded(
              child: listaFiltrada.isEmpty
                  ? const Center(child: Text('No se encontraron incidentes.'))
                  : ListView.builder(
                      itemCount: listaFiltrada.length,
                      itemBuilder: (context, index) {
                        final ticket = listaFiltrada[index];
                        return Card(
                          elevation: 2,
                          margin: const EdgeInsets.symmetric(vertical: 8),
                          child: ListTile(
                            contentPadding: const EdgeInsets.all(12),
                            title: Text(
                              '${ticket.id}: ${ticket.title}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Padding(
                              padding: const EdgeInsets.only(top: 8.0),
                              child: Text(
                                ticket.description,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            trailing: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Text(
                                  'Prioridad IA',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: Colors.grey,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 4,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.indigo.withAlpha(25),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: Colors.indigo),
                                  ),
                                  child: const Text(
                                    'Pendiente',
                                    style: TextStyle(
                                      color: Colors.indigo,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            onTap: () {},
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
