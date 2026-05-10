import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/incident.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';

class TechnicianResolvePage extends ConsumerStatefulWidget {
  final Incident ticket;

  const TechnicianResolvePage({super.key, required this.ticket});

  @override
  ConsumerState<TechnicianResolvePage> createState() => _TechnicianResolvePageState();
}

class _TechnicianResolvePageState extends ConsumerState<TechnicianResolvePage> {
  final _resolutionController = TextEditingController();

  @override
  void dispose() {
    _resolutionController.dispose();
    super.dispose();
  }

  Future<void> _resolveTicket() async {
    if (_resolutionController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Debes ingresar un reporte de solución antes de cerrar el ticket.')),
      );
      return;
    }

    final navigator = Navigator.of(context);
    final messenger = ScaffoldMessenger.of(context);
    await ref.read(incidentProvider.notifier).resolveIncident(widget.ticket.id, _resolutionController.text.trim());
    if (!context.mounted) {
      return;
    }
    navigator.pop();
    messenger.showSnackBar(
      SnackBar(content: Text('Ticket ${widget.ticket.id} resuelto correctamente', style: const TextStyle(fontWeight: FontWeight.bold))),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text(
          'Resolución - ${widget.ticket.id}',
          style: const TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800, fontSize: 18, letterSpacing: -0.5),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Detalles del Problema
            const Text('REPORTE ORIGINAL', style: TextStyle(color: Colors.black54, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.05)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(widget.ticket.title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF111827))),
                  const SizedBox(height: 12),
                  Text(widget.ticket.description, style: const TextStyle(fontSize: 15, color: Color(0xFF4B5563), height: 1.5)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Diagnóstico y Resolución
            const Text('INFORME DE SOLUCIÓN', style: TextStyle(color: Colors.black54, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
              ),
              child: TextField(
                controller: _resolutionController,
                maxLines: 6,
                decoration: const InputDecoration(
                  hintText: 'Describe el diagnóstico final y los pasos que seguiste para resolver el incidente...',
                  hintStyle: TextStyle(color: Colors.black38),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.all(16),
                ),
              ),
            ),
            
            const SizedBox(height: 40),
            
            // Botón de Cierre
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _resolveTicket,
                icon: const Icon(Icons.task_alt),
                label: const Text('Marcar como Resuelto', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981), // Verde éxito
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 0,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
