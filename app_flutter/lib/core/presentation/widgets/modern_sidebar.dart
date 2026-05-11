import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/utils/url_opener.dart';
import '../../../core/theme/theme_mode_provider.dart';
import '../../../features/client_portal/models/providers/client_portal_providers.dart';
import '../../../features/auth/providers/auth_providers.dart';
import '../../../features/analyst_dashboard/models/providers/analyst_providers.dart';
import '../../../features/technician_dashboard/models/providers/technician_providers.dart';
import '../../../features/client_portal/presentation/pages/client_profile_page.dart';
import '../../../features/analyst_dashboard/presentation/pages/analyst_settings_page.dart';

Future<void> _openGrafana(BuildContext context) async {
  try {
    await openExternalUrl('http://localhost:3001/login');
  } catch (e) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('No se pudo abrir Grafana: $e'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}

enum UserRole { client, analyst, admin, technician }

class ModernSidebar extends ConsumerWidget {
  final UserRole role;

  const ModernSidebar({super.key, this.role = UserRole.client});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cs = Theme.of(context).colorScheme;

    return Drawer(
      backgroundColor: cs.surface,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(cs),
            const SizedBox(height: 16),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                children: [
                  if (role == UserRole.client) ..._clientItems(context, ref, cs),
                  if (role == UserRole.analyst) ..._analystItems(context, ref, cs),
                  if (role == UserRole.technician) ..._technicianItems(context, ref, cs),
                  if (role == UserRole.admin) ..._adminItems(context, ref, cs),
                ],
              ),
            ),
            _ThemeToggleTile(cs: cs),
            _buildLogoutButton(context, ref, cs),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(ColorScheme cs) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Row(
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [cs.primary, cs.primary.withValues(alpha: 0.7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.flash_on, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 12),
          Text(
            'SIPIIT',
            style: TextStyle(
              color: cs.onSurface,
              fontSize: 20,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLogoutButton(BuildContext context, WidgetRef ref, ColorScheme cs) {
    return Container(
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.5))),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: _SidebarItem(
          icon: Icons.logout_rounded,
          title: 'Cerrar Sesión',
          color: cs.error,
          onTap: () => ref.read(authProvider.notifier).logout(),
        ),
      ),
    );
  }

  List<Widget> _clientItems(BuildContext context, WidgetRef ref, ColorScheme cs) {
    return [
      _SectionLabel(label: 'Navegación', cs: cs),
      const SizedBox(height: 4),
      const _ClientFilterExpansion(),
      const SizedBox(height: 4),
      _SidebarItem(
        icon: Icons.settings_outlined,
        title: 'Configuración',
        onTap: () {
          Navigator.pop(context);
          Navigator.push(context, MaterialPageRoute(builder: (context) => const ClientProfilePage()));
        },
      ),
    ];
  }

  List<Widget> _analystItems(BuildContext context, WidgetRef ref, ColorScheme cs) {
    return [
      _SectionLabel(label: 'Navegación', cs: cs),
      const SizedBox(height: 4),
      const _AnalystFilterExpansion(),
      const SizedBox(height: 4),
      _SidebarItem(
        icon: Icons.settings_outlined,
        title: 'Configuración',
        onTap: () {
          Navigator.pop(context);
          Navigator.push(context, MaterialPageRoute(builder: (context) => const AnalystSettingsPage()));
        },
      ),
      const SizedBox(height: 16),
      _SectionLabel(label: 'Herramientas', cs: cs),
      const SizedBox(height: 4),
      _SidebarItem(
        icon: Icons.bar_chart_rounded,
        title: 'Grafana',
        color: cs.primary,
        onTap: () {
          Navigator.pop(context);
          _openGrafana(context);
        },
      ),
    ];
  }

  List<Widget> _technicianItems(BuildContext context, WidgetRef ref, ColorScheme cs) {
    return [
      _SectionLabel(label: 'Navegación', cs: cs),
      const SizedBox(height: 4),
      const _TechnicianFilterExpansion(),
      const SizedBox(height: 4),
      _SidebarItem(
        icon: Icons.assignment_ind_outlined,
        title: 'Mis Tickets',
        isSelected: ref.watch(technicianFilterProvider) == 'Mis Tickets',
        onTap: () {
          ref.read(technicianFilterProvider.notifier).setFilter('Mis Tickets');
          Navigator.pop(context);
        },
      ),
    ];
  }

  List<Widget> _adminItems(BuildContext context, WidgetRef ref, ColorScheme cs) {
    return [
      _SectionLabel(label: 'Herramientas', cs: cs),
      const SizedBox(height: 4),
      _SidebarItem(
        icon: Icons.bar_chart_rounded,
        title: 'Grafana',
        color: cs.primary,
        onTap: () {
          Navigator.pop(context);
          _openGrafana(context);
        },
      ),
    ];
  }
}

// ── Theme Toggle Tile ──────────────────────────────────────────────────────────

class _ThemeToggleTile extends ConsumerWidget {
  const _ThemeToggleTile({required this.cs});
  final ColorScheme cs;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final notifier  = ref.read(themeModeProvider.notifier);
    final isDark    = themeMode == ThemeMode.dark;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Container(
        decoration: BoxDecoration(
          color: cs.surfaceContainerHighest.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Row(
            children: [
              Icon(
                isDark ? Icons.dark_mode_outlined : Icons.light_mode_outlined,
                size: 18,
                color: cs.onSurfaceVariant,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  isDark ? 'Modo Oscuro' : 'Modo Claro',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: cs.onSurfaceVariant,
                  ),
                ),
              ),
              // 3-way: light / system / dark
              Row(
                children: [
                  _ThemeBtn(
                    icon: Icons.light_mode_outlined,
                    tooltip: 'Claro',
                    selected: themeMode == ThemeMode.light,
                    onTap: notifier.setLight,
                    cs: cs,
                  ),
                  const SizedBox(width: 4),
                  _ThemeBtn(
                    icon: Icons.brightness_auto_outlined,
                    tooltip: 'Sistema',
                    selected: themeMode == ThemeMode.system,
                    onTap: notifier.setSystem,
                    cs: cs,
                  ),
                  const SizedBox(width: 4),
                  _ThemeBtn(
                    icon: Icons.dark_mode_outlined,
                    tooltip: 'Oscuro',
                    selected: themeMode == ThemeMode.dark,
                    onTap: notifier.setDark,
                    cs: cs,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ThemeBtn extends StatelessWidget {
  const _ThemeBtn({
    required this.icon,
    required this.tooltip,
    required this.selected,
    required this.onTap,
    required this.cs,
  });
  final IconData icon;
  final String tooltip;
  final bool selected;
  final VoidCallback onTap;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: tooltip,
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          width: 30,
          height: 30,
          decoration: BoxDecoration(
            color: selected ? cs.primaryContainer : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: selected ? cs.primary : Colors.transparent,
              width: 1.5,
            ),
          ),
          child: Icon(
            icon,
            size: 15,
            color: selected ? cs.primary : cs.onSurfaceVariant,
          ),
        ),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  final ColorScheme cs;

  const _SectionLabel({required this.label, required this.cs});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
      child: Text(
        label.toUpperCase(),
        style: TextStyle(
          color: cs.onSurfaceVariant.withValues(alpha: 0.6),
          fontSize: 11,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}

class _SidebarItem extends StatefulWidget {
  final IconData icon;
  final String title;
  final bool isSelected;
  final VoidCallback onTap;
  final Color? color;

  const _SidebarItem({
    required this.icon,
    required this.title,
    required this.onTap,
    this.isSelected = false,
    this.color,
  });

  @override
  State<_SidebarItem> createState() => _SidebarItemState();
}

class _SidebarItemState extends State<_SidebarItem> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final defaultColor = widget.isSelected ? cs.primary : cs.onSurfaceVariant;
    final color = widget.color ?? defaultColor;
    final bgColor = widget.isSelected
        ? cs.primaryContainer.withValues(alpha: 0.5)
        : (_isHovered ? cs.surfaceContainerHighest : Colors.transparent);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: InkWell(
        onTap: widget.onTap,
        borderRadius: BorderRadius.circular(10),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            children: [
              Icon(widget.icon, color: color, size: 20),
              const SizedBox(width: 14),
              Text(
                widget.title,
                style: TextStyle(
                  color: color,
                  fontSize: 14,
                  fontWeight: widget.isSelected ? FontWeight.w600 : FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ClientFilterExpansion extends ConsumerStatefulWidget {
  const _ClientFilterExpansion();
  @override
  ConsumerState<_ClientFilterExpansion> createState() => _ClientFilterExpansionState();
}

class _ClientFilterExpansionState extends ConsumerState<_ClientFilterExpansion> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final currentFilter = ref.watch(clientFilterProvider);

    return Column(
      children: [
        _SidebarItem(
          icon: Icons.confirmation_number_outlined,
          title: 'Incidentes',
          isSelected: _isExpanded || currentFilter != 'Todos',
          onTap: () => setState(() => _isExpanded = !_isExpanded),
        ),
        AnimatedCrossFade(
          firstChild: const SizedBox(height: 0, width: double.infinity),
          secondChild: Padding(
            padding: const EdgeInsets.only(left: 32, top: 4),
            child: Column(
              children: [
                _SubItem(title: 'Todos', isSelected: currentFilter == 'Todos', onTap: () {
                  ref.read(clientFilterProvider.notifier).setFilter('Todos');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Pendiente', isSelected: currentFilter == 'Pendiente', onTap: () {
                  ref.read(clientFilterProvider.notifier).setFilter('Pendiente');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'En Progreso', isSelected: currentFilter == 'En progreso', onTap: () {
                  ref.read(clientFilterProvider.notifier).setFilter('En progreso');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Resuelto', isSelected: currentFilter == 'Resuelto', onTap: () {
                  ref.read(clientFilterProvider.notifier).setFilter('Resuelto');
                  Navigator.pop(context);
                }),
              ],
            ),
          ),
          crossFadeState: _isExpanded ? CrossFadeState.showSecond : CrossFadeState.showFirst,
          duration: const Duration(milliseconds: 200),
        ),
      ],
    );
  }
}

class _AnalystFilterExpansion extends ConsumerStatefulWidget {
  const _AnalystFilterExpansion();
  @override
  ConsumerState<_AnalystFilterExpansion> createState() => _AnalystFilterExpansionState();
}

class _AnalystFilterExpansionState extends ConsumerState<_AnalystFilterExpansion> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final currentFilter = ref.watch(analystFilterProvider);

    return Column(
      children: [
        _SidebarItem(
          icon: Icons.inbox_outlined,
          title: 'Incidentes',
          isSelected: _isExpanded || currentFilter != 'Todas',
          onTap: () => setState(() => _isExpanded = !_isExpanded),
        ),
        AnimatedCrossFade(
          firstChild: const SizedBox(height: 0, width: double.infinity),
          secondChild: Padding(
            padding: const EdgeInsets.only(left: 32, top: 4),
            child: Column(
              children: [
                _SubItem(title: 'Todas', isSelected: currentFilter == 'Todas', onTap: () {
                  ref.read(analystFilterProvider.notifier).setFilter('Todas');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Crítica', isSelected: currentFilter == 'Crítica', onTap: () {
                  ref.read(analystFilterProvider.notifier).setFilter('Crítica');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Alta', isSelected: currentFilter == 'Alta', onTap: () {
                  ref.read(analystFilterProvider.notifier).setFilter('Alta');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Media', isSelected: currentFilter == 'Media', onTap: () {
                  ref.read(analystFilterProvider.notifier).setFilter('Media');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Baja', isSelected: currentFilter == 'Baja', onTap: () {
                  ref.read(analystFilterProvider.notifier).setFilter('Baja');
                  Navigator.pop(context);
                }),
              ],
            ),
          ),
          crossFadeState: _isExpanded ? CrossFadeState.showSecond : CrossFadeState.showFirst,
          duration: const Duration(milliseconds: 200),
        ),
      ],
    );
  }
}

class _TechnicianFilterExpansion extends ConsumerStatefulWidget {
  const _TechnicianFilterExpansion();
  @override
  ConsumerState<_TechnicianFilterExpansion> createState() => _TechnicianFilterExpansionState();
}

class _TechnicianFilterExpansionState extends ConsumerState<_TechnicianFilterExpansion> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final currentFilter = ref.watch(technicianFilterProvider);

    return Column(
      children: [
        _SidebarItem(
          icon: Icons.build_outlined,
          title: 'Tickets del Departamento',
          isSelected: _isExpanded || currentFilter != 'Todos',
          onTap: () => setState(() => _isExpanded = !_isExpanded),
        ),
        AnimatedCrossFade(
          firstChild: const SizedBox(height: 0, width: double.infinity),
          secondChild: Padding(
            padding: const EdgeInsets.only(left: 32, top: 4),
            child: Column(
              children: [
                _SubItem(title: 'Todos', isSelected: currentFilter == 'Todos', onTap: () {
                  ref.read(technicianFilterProvider.notifier).setFilter('Todos');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Nuevo', isSelected: currentFilter == 'Nuevo', onTap: () {
                  ref.read(technicianFilterProvider.notifier).setFilter('Nuevo');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Pendiente', isSelected: currentFilter == 'Pendiente', onTap: () {
                  ref.read(technicianFilterProvider.notifier).setFilter('Pendiente');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'En Progreso', isSelected: currentFilter == 'En Progreso', onTap: () {
                  ref.read(technicianFilterProvider.notifier).setFilter('En Progreso');
                  Navigator.pop(context);
                }),
                _SubItem(title: 'Resuelto', isSelected: currentFilter == 'Resuelto', onTap: () {
                  ref.read(technicianFilterProvider.notifier).setFilter('Resuelto');
                  Navigator.pop(context);
                }),
              ],
            ),
          ),
          crossFadeState: _isExpanded ? CrossFadeState.showSecond : CrossFadeState.showFirst,
          duration: const Duration(milliseconds: 200),
        ),
      ],
    );
  }
}

class _SubItem extends StatelessWidget {
  final String title;
  final bool isSelected;
  final VoidCallback onTap;

  const _SubItem({
    required this.title,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
        decoration: BoxDecoration(
          color: isSelected ? cs.primaryContainer.withValues(alpha: 0.5) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          title,
          style: TextStyle(
            color: isSelected ? cs.primary : cs.onSurfaceVariant,
            fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}
