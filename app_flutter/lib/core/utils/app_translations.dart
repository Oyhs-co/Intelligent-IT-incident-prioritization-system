import 'package:flutter/material.dart';


class AppTranslations {
 

  static String status(String raw) {
    switch (raw.toLowerCase().trim()) {
      case 'new':         return 'Nuevo';
      case 'open':        return 'Abierto';
      case 'pending':     return 'Pendiente';
      case 'in_progress': return 'En Progreso';
      case 'resolved':    return 'Resuelto';
      case 'closed':      return 'Cerrado';
      case 'rejected':    return 'Rechazado';
      case 'cancelled':   return 'Cancelado';
      case 'on_hold':     return 'En Espera';
      case 'escalated':   return 'Escalado';
      default:            return _cap(raw);
    }
  }

  
  static String priority(String? raw) {
    if (raw == null || raw.isEmpty) return 'Sin clasificar';
    switch (raw.toLowerCase().trim()) {
      case 'critical':
      case 'crítica':
      case 'critica':
      case 'p4 (critical)':  return 'Crítica';
      case 'high':
      case 'alta':
      case 'p3 (high)':      return 'Alta';
      case 'medium':
      case 'media':
      case 'p2 (medium)':    return 'Media';
      case 'low':
      case 'baja':
      case 'p1 (low)':       return 'Baja';
      default:               return _cap(raw);
    }
  }

  
  static String category(String? raw) {
    if (raw == null || raw.isEmpty) return 'General';
    switch (raw.toLowerCase().trim()) {
      case 'hardware':  return 'Hardware';
      case 'software':  return 'Software';
      case 'network':   return 'Red';
      case 'security':  return 'Seguridad';
      case 'other':     return 'Otro';
      default:          return _cap(raw);
    }
  }

  
  static String role(String raw) {
    switch (raw.toLowerCase().trim()) {
      case 'admin':       return 'Administrador';
      case 'analyst':     return 'Analista';
      case 'technician':  return 'Técnico';
      case 'user':
      case 'client':      return 'Cliente';
      default:            return _cap(raw);
    }
  }

  
  static StatusChipStyle statusStyle(String raw) {
    switch (raw.toLowerCase().trim()) {
      case 'resolved':
      case 'closed':
        return const StatusChipStyle(Color(0xFF059669), Color(0xFFD1FAE5), Color(0xFF065F46));
      case 'in_progress':
        return const StatusChipStyle(Color(0xFF2563EB), Color(0xFFDBEAFE), Color(0xFF1E3A8A));
      case 'pending':
      case 'open':
        return const StatusChipStyle(Color(0xFF7C3AED), Color(0xFFEDE9FE), Color(0xFF4C1D95));
      case 'new':
        return const StatusChipStyle(Color(0xFF0D9488), Color(0xFFCCFBF1), Color(0xFF134E4A));
      case 'rejected':
      case 'cancelled':
        return const StatusChipStyle(Color(0xFFDC2626), Color(0xFFFEE2E2), Color(0xFF7F1D1D));
      case 'on_hold':
      case 'escalated':
        return const StatusChipStyle(Color(0xFFD97706), Color(0xFFFEF3C7), Color(0xFF78350F));
      default:
        return const StatusChipStyle(Color(0xFF6B7280), Color(0xFFF3F4F6), Color(0xFF374151));
    }
  }

  

  static PriorityChipStyle priorityStyle(String? raw) {
    switch (priority(raw ?? '').toLowerCase()) {
      case 'crítica':
        return const PriorityChipStyle(Color(0xFF7F1D1D), Color(0xFFFEE2E2), Color(0xFF991B1B));
      case 'alta':
        return const PriorityChipStyle(Color(0xFF991B1B), Color(0xFFFEE2E2), Color(0xFFDC2626));
      case 'media':
        return const PriorityChipStyle(Color(0xFF78350F), Color(0xFFFEF3C7), Color(0xFFD97706));
      case 'baja':
        return const PriorityChipStyle(Color(0xFF065F46), Color(0xFFD1FAE5), Color(0xFF059669));
      default:
        return const PriorityChipStyle(Color(0xFF374151), Color(0xFFF3F4F6), Color(0xFF6B7280));
    }
  }

  static String _cap(String s) =>
      s.isEmpty ? s : s[0].toUpperCase() + s.substring(1).toLowerCase();
}



class StatusChipStyle {
  final Color accent;
  final Color background;
  final Color text;
  const StatusChipStyle(this.accent, this.background, this.text);
}

class PriorityChipStyle {
  final Color dark;
  final Color background;
  final Color accent;
  const PriorityChipStyle(this.dark, this.background, this.accent);
}



class StatusChip extends StatelessWidget {
  const StatusChip({super.key, required this.status});
  final String status;

  @override
  Widget build(BuildContext context) {
    final style = AppTranslations.statusStyle(status);
    return _Chip(
      label: AppTranslations.status(status),
      background: style.background,
      textColor: style.text,
    );
  }
}

class PriorityChip extends StatelessWidget {
  const PriorityChip({super.key, required this.priority, this.leftBorder = false});
  final String? priority;
  final bool leftBorder;

  @override
  Widget build(BuildContext context) {
    final label = AppTranslations.priority(priority);
    final style = AppTranslations.priorityStyle(priority);
    return _Chip(
      label: label.toUpperCase(),
      background: style.background,
      textColor: style.dark,
      border: Border.all(color: style.accent.withValues(alpha: 0.4)),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({
    required this.label,
    required this.background,
    required this.textColor,
    this.border,
  });
  final String label;
  final Color background;
  final Color textColor;
  final BoxBorder? border;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(20),
        border: border,
      ),
      child: Text(
        label,
        style: TextStyle(
          color: textColor,
          fontSize: 11,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}
