import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/client_portal/models/incident.dart';
import '../../../../features/client_portal/models/providers/client_portal_providers.dart';

class IncidentReviewPage extends ConsumerStatefulWidget {
  final Incident ticket;

  const IncidentReviewPage({super.key, required this.ticket});

  @override
  ConsumerState<IncidentReviewPage> createState() => _IncidentReviewPageState();
}

class _IncidentReviewPageState extends ConsumerState<IncidentReviewPage> {
  late String areaSeleccionada;
  late String prioridadSeleccionada;

  final areas = ['Redes', 'Soporte de Hardware', 'Cuentas y Accesos', 'Desarrollo de Software', 'Bases de Datos', 'Soporte General'];
  final prioridades = ['Alta', 'Media', 'Baja'];

  @override
  void initState() {
    super.initState();
    areaSeleccionada = widget.ticket.assignedArea ?? widget.ticket.aiSuggestedArea;
    prioridadSeleccionada = widget.ticket.aiPriority;
    
    if (!areas.contains(areaSeleccionada)) areas.add(areaSeleccionada);
    if (!prioridades.contains(prioridadSeleccionada)) prioridades.add(prioridadSeleccionada);
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
          'Revisión - ${widget.ticket.id}',
          style: const TextStyle(
            color: Color(0xFF111827),
            fontWeight: FontWeight.w800,
            fontSize: 18,
            letterSpacing: -0.5,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Contenedor de Detalles
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
                boxShadow: [
                  BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 12, offset: const Offset(0, 6)),
                ],
              ),
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('TÍTULO DEL PROBLEMA', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 8),
                  Text(widget.ticket.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF111827), height: 1.2)),
                  const Padding(padding: EdgeInsets.symmetric(vertical: 24), child: Divider(height: 1, thickness: 1, color: Color(0xFFF3F4F6))),
                  const Text('DESCRIPCIÓN', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 12),
                  Text(widget.ticket.description, style: const TextStyle(fontSize: 16, color: Color(0xFF374151), height: 1.6)),
                ],
              ),
            ),
            
            const SizedBox(height: 24),

            // Contenedor de IA
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF2563EB).withValues(alpha: 0.2), width: 1.5),
                boxShadow: [
                  BoxShadow(color: const Color(0xFF2563EB).withValues(alpha: 0.05), blurRadius: 12, offset: const Offset(0, 6)),
                ],
              ),
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.auto_awesome, color: Color(0xFF2563EB)),
                      const SizedBox(width: 8),
                      const Text('Análisis Inicial de IA', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(8)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text('• Prioridad sugerida: ${widget.ticket.aiPriority}', style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                        const SizedBox(height: 8),
                        Text('• Área técnica sugerida: ${widget.ticket.aiSuggestedArea}', style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A))),
                      ],
                    ),
                  )
                ],
              ),
            ),
            
            const SizedBox(height: 24),

            // Contenedor de Triage (Decisión humana)
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
                boxShadow: [
                  BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 12, offset: const Offset(0, 6)),
                ],
              ),
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Decisión del Analista (Triage)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
                  const SizedBox(height: 24),
                  
                  const Text('PRIORIDAD FINAL', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                    ),
                    initialValue: prioridadSeleccionada,
                    items: prioridades.map((p) => DropdownMenuItem(value: p, child: Text(p))).toList(),
                    onChanged: (val) => setState(() => prioridadSeleccionada = val!),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  const Text('ÁREA TÉCNICA ENCARGADA', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF6B7280))),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                    ),
                    initialValue: areaSeleccionada,
                    items: areas.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
                    onChanged: (val) => setState(() => areaSeleccionada = val!),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            ElevatedButton(
              onPressed: () {
                ref.read(incidentProvider.notifier).assignAndEditTicket(widget.ticket.id, areaSeleccionada, prioridadSeleccionada);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Ticket asignado a $areaSeleccionada')));
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0F172A),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                elevation: 0,
              ),
              child: const Text('Guardar y Enviar a Área', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
