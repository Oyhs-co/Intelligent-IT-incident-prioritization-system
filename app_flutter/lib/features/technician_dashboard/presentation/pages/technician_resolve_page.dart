import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/utils/app_translations.dart';
import '../../../client_portal/models/incident.dart';
import '../../../client_portal/models/providers/client_portal_providers.dart';

class TechnicianResolvePage extends ConsumerStatefulWidget {
  final Incident ticket;
  const TechnicianResolvePage({super.key, required this.ticket});
  @override
  ConsumerState<TechnicianResolvePage> createState() => _TechnicianResolvePageState();
}

class _TechnicianResolvePageState extends ConsumerState<TechnicianResolvePage> {
  final _formKey        = GlobalKey<FormState>();
  final _resolutionCtrl = TextEditingController();
  String _resolutionCode = 'fixed';
  bool _loading = false;

  static const _codes = {
    'fixed': 'Problema corregido',
    'workaround': 'Solución temporal',
    'no_action': 'Sin acción requerida',
    'duplicate': 'Ticket duplicado',
    'not_reproducible': 'No reproducible',
  };

  @override
  void dispose() {
    _resolutionCtrl.dispose();
    super.dispose();
  }

  Future<void> _startProgress() async {
    setState(() => _loading = true);
    try {
      await ref.read(incidentProvider.notifier).updateIncident(widget.ticket.id, {'status': 'in_progress'});
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: const Text('Ticket tomado — En Progreso'),
        backgroundColor: const Color(0xFF2563EB),
        behavior: SnackBarBehavior.floating,
      ));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e'), behavior: SnackBarBehavior.floating));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _resolve() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await ref.read(incidentProvider.notifier).resolveIncident(widget.ticket.id, _resolutionCtrl.text.trim());
      if (!mounted) return;
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('✓ ${widget.ticket.ticketNumber} resuelto'),
        backgroundColor: const Color(0xFF059669),
        behavior: SnackBarBehavior.floating,
      ));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e'), behavior: SnackBarBehavior.floating));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs     = Theme.of(context).colorScheme;
    final t      = widget.ticket;
    final status = t.status.toLowerCase();
    final isNew  = ['new','open','pending'].contains(status);
    final isDone = ['resolved','closed'].contains(status);
    final pStyle = AppTranslations.priorityStyle(t.finalPriority ?? t.priorityLabel);
    final sStyle = AppTranslations.statusStyle(t.status);

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(title: Text(t.ticketNumber), centerTitle: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ── Ticket card ────────────────────────────────────────────
                _Card(cs: cs, child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Row(children: [
                    _Pill(AppTranslations.status(t.status), sStyle.background, sStyle.text),
                    const SizedBox(width: 6),
                    _Pill(AppTranslations.priority(t.finalPriority ?? t.priorityLabel), pStyle.background, pStyle.dark),
                    const Spacer(),
                    if (t.isSlaBreached) _Pill('SLA Incumplido', cs.errorContainer, cs.error),
                  ]),
                  const SizedBox(height: 12),
                  Text(t.title, style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: cs.onSurface)),
                  const SizedBox(height: 8),
                  Text(t.description, style: TextStyle(fontSize: 13, color: cs.onSurfaceVariant, height: 1.5)),
                  const SizedBox(height: 12),
                  Wrap(spacing: 8, runSpacing: 6, children: [
                    _Tag(Icons.folder_outlined, AppTranslations.category(t.category), cs),
                    _Tag(Icons.bolt_outlined, 'Urgencia ${t.urgency}/5', cs),
                    _Tag(Icons.people_outline, 'Impacto ${t.impact}/5', cs),
                    if (t.slaDeadline != null) _Tag(Icons.schedule_outlined, 'SLA: ${_fmt(t.slaDeadline!)}', cs),
                  ]),
                  ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(color: pStyle.background.withValues(alpha: 0.5), borderRadius: BorderRadius.circular(8)),
                      child: Row(children: [
                        Icon(Icons.flag_outlined, size: 13, color: pStyle.accent),
                        const SizedBox(width: 6),
                        Expanded(child: Text(
                          'Prioridad asignada: ${AppTranslations.priority(t.finalPriority ?? t.priorityLabel)}',
                          style: TextStyle(fontSize: 12, color: pStyle.dark, fontWeight: FontWeight.w700),
                        )),
                      ]),
                    ),
                  ],
                ])),
                const SizedBox(height: 14),

                // ── Take ticket ────────────────────────────────────────────
                if (isNew && !isDone)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 14),
                    child: OutlinedButton.icon(
                      onPressed: _loading ? null : _startProgress,
                      icon: const Icon(Icons.play_circle_outline, size: 18),
                      label: const Text('Tomar Ticket — Iniciar En Progreso'),
                    ),
                  ),

                // ── Done notice ────────────────────────────────────────────
                if (isDone)
                  Container(
                    margin: const EdgeInsets.only(bottom: 14),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFF10B981)),
                    ),
                    child: Row(children: [
                      const Icon(Icons.check_circle, color: Color(0xFF059669)),
                      const SizedBox(width: 10),
                      const Text('Este ticket ya fue resuelto.',
                          style: TextStyle(color: Color(0xFF065F46), fontWeight: FontWeight.w700)),
                    ]),
                  ),

                // ── Resolution form ────────────────────────────────────────
                if (!isDone) ...[
                  _Card(cs: cs, child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('INFORME DE SOLUCIÓN',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 1.2, color: cs.onSurfaceVariant)),
                    const SizedBox(height: 14),
                    DropdownButtonFormField<String>(
                      initialValue: _resolutionCode,
                      decoration: const InputDecoration(labelText: 'Código de Resolución'),
                      items: _codes.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
                      onChanged: (v) => setState(() => _resolutionCode = v!),
                    ),
                    const SizedBox(height: 14),
                    TextFormField(
                      controller: _resolutionCtrl,
                      maxLines: 5,
                      validator: (v) {
                        if (v == null || v.trim().isEmpty) return 'Ingresa la descripción de la solución.';
                        if (v.trim().length < 20) return 'Mínimo 20 caracteres.';
                        return null;
                      },
                      decoration: const InputDecoration(
                        labelText: 'Descripción de la Solución',
                        alignLabelWithHint: true,
                        hintText: 'Diagnóstico, pasos aplicados y resultado...',
                      ),
                    ),
                  ])),
                  const SizedBox(height: 16),
                  _loading
                      ? const Center(child: CircularProgressIndicator())
                      : FilledButton.icon(
                          onPressed: _resolve,
                          icon: const Icon(Icons.task_alt_outlined, size: 18),
                          label: const Text('Resolver Ticket'),
                          style: FilledButton.styleFrom(
                            backgroundColor: const Color(0xFF059669),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                        ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  static String _fmt(String d) {
    try {
      final dt = DateTime.parse(d);
      const m = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
      return '${dt.day} ${m[dt.month - 1]}';
    } catch (_) { return d; }
  }
}

class _Card extends StatelessWidget {
  const _Card({required this.cs, required this.child});
  final ColorScheme cs;
  final Widget child;
  @override
  Widget build(BuildContext context) => Container(
    width: double.infinity, padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: cs.surface, borderRadius: BorderRadius.circular(14),
      border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
      boxShadow: [BoxShadow(color: cs.shadow.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 3))],
    ),
    child: child,
  );
}

class _Pill extends StatelessWidget {
  const _Pill(this.label, this.bg, this.fg);
  final String label; final Color bg, fg;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(20)),
    child: Text(label, style: TextStyle(color: fg, fontSize: 10, fontWeight: FontWeight.w800)),
  );
}

class _Tag extends StatelessWidget {
  const _Tag(this.icon, this.label, this.cs);
  final IconData icon; final String label; final ColorScheme cs;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    decoration: BoxDecoration(color: cs.surfaceContainerHighest, borderRadius: BorderRadius.circular(8)),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, size: 11, color: cs.onSurfaceVariant),
      const SizedBox(width: 4),
      Text(label, style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant, fontWeight: FontWeight.w600)),
    ]),
  );
}
