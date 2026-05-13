import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/utils/app_constants.dart';

class AnalystDirectoryPage extends ConsumerStatefulWidget {
  const AnalystDirectoryPage({super.key});

  @override
  ConsumerState<AnalystDirectoryPage> createState() => _AnalystDirectoryPageState();
}

class _AnalystDirectoryPageState extends ConsumerState<AnalystDirectoryPage> {
  final ApiClient _api = ApiClient();
  List<Map<String, dynamic>> _users = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchUsers();
  }

  Future<void> _fetchUsers() async {
    setState(() => _loading = true);
    try {
      final data = await _api.request('GET', ApiEndpoints.users, auth: true) as Map<String, dynamic>;
      final items = (data['items'] as List<dynamic>).cast<Map<String, dynamic>>();
      setState(() {
        _users = items.where((u) => u['role'] == 'technician').toList();
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error al cargar el directorio: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        title: const Text('Directorio Técnico'),
      ),
      body: _buildBody(cs),
    );
  }

  Widget _buildBody(ColorScheme cs) {
    if (_loading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: cs.primary),
            const SizedBox(height: 16),
            Text('Cargando...', style: TextStyle(color: cs.onSurfaceVariant)),
          ],
        ),
      );
    }
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, size: 48, color: cs.error),
            const SizedBox(height: 16),
            Text(_error!, textAlign: TextAlign.center, style: TextStyle(color: cs.onSurfaceVariant)),
            const SizedBox(height: 16),
            FilledButton.icon(
              icon: const Icon(Icons.refresh_outlined, size: 16),
              label: const Text('Reintentar'),
              onPressed: _fetchUsers,
            ),
          ],
        ),
      );
    }
    if (_users.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people_outline, size: 56, color: cs.outlineVariant),
            const SizedBox(height: 16),
            Text('No hay técnicos registrados.', style: TextStyle(color: cs.onSurfaceVariant)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _fetchUsers,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _users.length,
        itemBuilder: (context, index) {
          final user = _users[index];
          final name = user['full_name'] as String? ?? user['username'] as String;
          final department = user['department'] as String? ?? 'Sin departamento';
          final isActive = user['is_active'] as bool? ?? true;

          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: (isActive ? const Color(0xFFDEF7EC) : cs.surfaceContainerHighest),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.person,
                      color: isActive ? const Color(0xFF03543F) : cs.onSurfaceVariant,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(name, style: TextStyle(fontWeight: FontWeight.w600, color: cs.onSurface, fontSize: 14)),
                        const SizedBox(height: 4),
                        Text(department, style: TextStyle(color: cs.onSurfaceVariant, fontWeight: FontWeight.w500, fontSize: 13)),
                        Row(
                          children: [
                            Container(
                              width: 6,
                              height: 6,
                              decoration: BoxDecoration(
                                color: isActive ? const Color(0xFF059669) : cs.onSurfaceVariant,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              isActive ? 'Activo' : 'Inactivo',
                              style: TextStyle(
                                color: isActive ? const Color(0xFF059669) : cs.onSurfaceVariant,
                                fontWeight: FontWeight.w600,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: cs.primaryContainer,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Técnico',
                      style: TextStyle(color: cs.onPrimaryContainer, fontWeight: FontWeight.w600, fontSize: 11),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
