import 'package:flutter/material.dart';

class ClientProfilePage extends StatefulWidget {
  const ClientProfilePage({super.key});

  @override
  State<ClientProfilePage> createState() => _ClientProfilePageState();
}

class _ClientProfilePageState extends State<ClientProfilePage> {
  bool notificacionesEmail = true;
  bool notificacionesPush = false;
  
  late TextEditingController _nameController;
  late TextEditingController _phoneController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: 'Juan Pérez');
    _phoneController = TextEditingController(text: '+52 555 123 4567');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: const Text('Mi Perfil y Ajustes', style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.w800)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const CircleAvatar(
              radius: 50,
              backgroundColor: Color(0xFF2563EB),
              child: Icon(Icons.person, size: 50, color: Colors.white),
            ),
            const SizedBox(height: 16),
            const Text('Juan Pérez', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const Text('cliente@test.com', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 32),
            _buildSection(
              title: 'Información Personal',
              child: Column(
                children: [
                  TextField(
                    decoration: const InputDecoration(labelText: 'Nombre Completo', border: OutlineInputBorder()),
                    controller: _nameController,
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    decoration: const InputDecoration(labelText: 'Teléfono', border: OutlineInputBorder()),
                    controller: _phoneController,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            _buildSection(
              title: 'Preferencias de Notificación',
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Notificaciones por Correo'),
                    subtitle: const Text('Recibe alertas sobre el estado de tus tickets.'),
                    value: notificacionesEmail,
                    onChanged: (val) => setState(() => notificacionesEmail = val),
                    activeTrackColor: const Color(0xFF2563EB).withValues(alpha: 0.5),
                    activeThumbColor: const Color(0xFF2563EB),
                  ),
                  const Divider(),
                  SwitchListTile(
                    title: const Text('Notificaciones Push'),
                    subtitle: const Text('Recibe alertas en tu dispositivo móvil.'),
                    value: notificacionesPush,
                    onChanged: (val) => setState(() => notificacionesPush = val),
                    activeTrackColor: const Color(0xFF2563EB).withValues(alpha: 0.5),
                    activeThumbColor: const Color(0xFF2563EB),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F172A),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Perfil actualizado')));
                  Navigator.pop(context);
                },
                child: const Text('Guardar Cambios', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({required String title, required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withValues(alpha: 0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF111827))),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }
}
