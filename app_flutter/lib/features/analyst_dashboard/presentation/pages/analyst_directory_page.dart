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
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text('Directorio Técnico', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800)),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.black54)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _fetchUsers, child: const Text('Reintentar')),
          ],
        ),
      );
    }
    if (_users.isEmpty) {
      return const Center(child: Text('No hay técnicos registrados.', style: TextStyle(color: Colors.black54)));
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

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: Colors.black.withValues(alpha: 0.08)),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: CircleAvatar(
                backgroundColor: (isActive ? Colors.green : Colors.grey).withValues(alpha: 0.1),
                child: Icon(Icons.person, color: isActive ? Colors.green : Colors.grey),
              ),
              title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  Text(department, style: TextStyle(color: Colors.grey.shade600, fontWeight: FontWeight.w600)),
                  Text(
                    isActive ? 'Activo' : 'Inactivo',
                    style: TextStyle(color: isActive ? Colors.green : Colors.grey, fontWeight: FontWeight.w600, fontSize: 12),
                  ),
                ],
              ),
              trailing: Text(
                user['role'] as String? ?? '',
                style: const TextStyle(color: Colors.black45, fontWeight: FontWeight.w600, fontSize: 12),
              ),
            ),
          );
        },
      ),
    );
  }
}
