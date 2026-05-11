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
        const SnackBar(
          content: Text('Debes ingresar un reporte de solución antes de cerrar el ticket.'),
          behavior: SnackBarBehavior.floating,
        ),
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
      SnackBar(
        content: Text('Ticket ${widget.ticket.ticketNumber} resuelto correctamente', style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF059669),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: Text('Resolución - ${widget.ticket.ticketNumber}'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Reporte Original', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1)),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: cs.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(widget.ticket.title, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: cs.onSurface)),
                  const SizedBox(height: 12),
                  Text(widget.ticket.description, style: TextStyle(fontSize: 15, color: cs.onSurface, height: 1.5)),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text('Informe de Solución', style: TextStyle(color: cs.onSurfaceVariant, fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 1)),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: cs.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
              ),
              child: TextField(
                controller: _resolutionController,
                maxLines: 6,
                decoration: InputDecoration(
                  hintText: 'Describe el diagnóstico final y los pasos que seguiste para resolver el incidente...',
                  hintStyle: TextStyle(color: cs.onSurfaceVariant.withValues(alpha: 0.5)),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.all(16),
                ),
              ),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _resolveTicket,
                icon: const Icon(Icons.task_alt),
                label: const Text('Marcar Como Resuelto', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981),
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
