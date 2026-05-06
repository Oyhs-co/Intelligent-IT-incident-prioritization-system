import 'package:flutter/material.dart';
import '../../models/incident.dart';
class IncidentDetailsPage extends StatelessWidget {
  final Incident incident;
  const IncidentDetailsPage({super.key, required this.incident});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Detalle de ${incident.id}')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Card(
          elevation: 4, 
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize
                  .min, 
              children: [
                Text(
                  'Título:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
                ),
                Text(
                  incident.title,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Divider(height: 30), 
                Text(
                  'Estado actual:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 5),
                Chip(
                  label: Text(
                    incident.status,
                    style: const TextStyle(color: Colors.white),
                  ),
                  backgroundColor: Colors.blueAccent,
                ),
                const Divider(height: 30),
                Text(
                  'Descripción reportada:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  incident.description.isEmpty
                      ? 'Sin descripción detallada.'
                      : incident.description,
                  style: const TextStyle(fontSize: 16),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

