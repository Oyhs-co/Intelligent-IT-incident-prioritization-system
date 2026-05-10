import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../features/client_portal/models/providers/client_portal_providers.dart';
import '../../../features/auth/presentation/pages/login_page.dart';
import '../../../features/client_portal/presentation/pages/client_profile_page.dart';
import '../../../features/analyst_dashboard/presentation/pages/analyst_settings_page.dart';

enum UserRole { client, analyst, admin }

class ModernSidebar extends StatelessWidget {
  final UserRole role;

  const ModernSidebar({super.key, this.role = UserRole.client});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: Colors.white,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: const Color(0xFF2563EB),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.flash_on, color: Colors.white, size: 20),
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    'sipiit',
                    style: TextStyle(
                      color: Color(0xFF111827),
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.0,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                children: [
                  if (role == UserRole.client) ...[
                    const _ClientFilterExpansion(),
                    const SizedBox(height: 4),
                    _SidebarItem(icon: Icons.person_outline, title: 'mi perfil / ajustes', isSelected: false, onTap: () {
                      Navigator.pop(context);
                      Navigator.push(context, MaterialPageRoute(builder: (context) => const ClientProfilePage()));
                    }),
                  ] else if (role == UserRole.analyst) ...[
                    const _AnalystFilterExpansion(),
                    const SizedBox(height: 4),
                    _SidebarItem(icon: Icons.manage_accounts_outlined, title: 'configuración de perfil', isSelected: false, onTap: () {
                      Navigator.pop(context);
                      Navigator.push(context, MaterialPageRoute(builder: (context) => const AnalystSettingsPage()));
                    }),
                  ] else if (role == UserRole.admin) ...[
                    _SidebarItem(icon: Icons.dashboard_outlined, title: 'panel principal', isSelected: true, onTap: () {}),
                    const SizedBox(height: 4),
                    _SidebarItem(icon: Icons.people_outline, title: 'gestión de usuarios', isSelected: false, onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Navegando a Usuarios...')));
                    }),
                    const SizedBox(height: 4),
                    _SidebarItem(icon: Icons.analytics_outlined, title: 'reportes y métricas', isSelected: false, onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Navegando a Reportes...')));
                    }),
                    const SizedBox(height: 4),
                    _SidebarItem(icon: Icons.settings_outlined, title: 'configuraciones', isSelected: false, onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Navegando a Configuraciones...')));
                    }),
                  ],
                ],
              ),
            ),
            const Divider(color: Color(0xFFE5E7EB)),
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: _SidebarItem(
                icon: Icons.logout,
                title: 'cerrar sesion',
                color: const Color(0xFFF87171),
                onTap: () {
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(builder: (context) => const LoginPage()),
                    (route) => false,
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
    final defaultColor = widget.isSelected ? const Color(0xFF2563EB) : const Color(0xFF6B7280);
    final color = widget.color ?? defaultColor;
    final bgColor = widget.isSelected 
        ? const Color(0xFFEFF6FF) 
        : (_isHovered ? const Color(0xFFF3F4F6) : Colors.transparent);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: InkWell(
        onTap: widget.onTap,
        borderRadius: BorderRadius.circular(8),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(widget.icon, color: color, size: 20),
              const SizedBox(width: 16),
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
          title: 'mis incidentes',
          isSelected: _isExpanded || currentFilter != 'Todos',
          onTap: () {
            setState(() {
              _isExpanded = !_isExpanded;
            });
          },
        ),
        AnimatedCrossFade(
          firstChild: const SizedBox(height: 0, width: double.infinity),
          secondChild: Padding(
            padding: const EdgeInsets.only(left: 32, top: 4),
            child: Column(
              children: [
                _SubItem(title: 'Todos', isSelected: currentFilter == 'Todos', onTap: () { ref.read(clientFilterProvider.notifier).setFilter('Todos'); Navigator.pop(context); }),
                _SubItem(title: 'Pendiente', isSelected: currentFilter == 'Pendiente', onTap: () { ref.read(clientFilterProvider.notifier).setFilter('Pendiente'); Navigator.pop(context); }),
                _SubItem(title: 'En progreso', isSelected: currentFilter == 'En progreso', onTap: () { ref.read(clientFilterProvider.notifier).setFilter('En progreso'); Navigator.pop(context); }),
                _SubItem(title: 'Resuelto', isSelected: currentFilter == 'Resuelto', onTap: () { ref.read(clientFilterProvider.notifier).setFilter('Resuelto'); Navigator.pop(context); }),
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
          title: 'bandeja de triage',
          isSelected: _isExpanded || currentFilter != 'Todas',
          onTap: () {
            setState(() {
              _isExpanded = !_isExpanded;
            });
          },
        ),
        AnimatedCrossFade(
          firstChild: const SizedBox(height: 0, width: double.infinity),
          secondChild: Padding(
            padding: const EdgeInsets.only(left: 32, top: 4),
            child: Column(
              children: [
                _SubItem(title: 'Todas', isSelected: currentFilter == 'Todas', onTap: () { ref.read(analystFilterProvider.notifier).setFilter('Todas'); Navigator.pop(context); }),
                _SubItem(title: 'Alta Prioridad', isSelected: currentFilter == 'Alta', onTap: () { ref.read(analystFilterProvider.notifier).setFilter('Alta'); Navigator.pop(context); }),
                _SubItem(title: 'Media Prioridad', isSelected: currentFilter == 'Media', onTap: () { ref.read(analystFilterProvider.notifier).setFilter('Media'); Navigator.pop(context); }),
                _SubItem(title: 'Baja Prioridad', isSelected: currentFilter == 'Baja', onTap: () { ref.read(analystFilterProvider.notifier).setFilter('Baja'); Navigator.pop(context); }),
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

  const _SubItem({required this.title, required this.isSelected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFEFF6FF) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          title,
          style: TextStyle(
            color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF6B7280),
            fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}
