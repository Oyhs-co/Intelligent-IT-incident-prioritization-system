import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/auth_providers.dart';
import '../widgets/auth_input_field.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _emailController = TextEditingController();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _departmentController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _departmentController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    final email = _emailController.text.trim();
    final username = _usernameController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Email, usuario y contraseña son requeridos')),
      );
      return;
    }

    ref.read(authProvider.notifier).register(
      email: email,
      username: username,
      password: password,
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      department: _departmentController.text.trim(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    ref.listen(authProvider, (previous, next) {
      if (next.error != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.error!), backgroundColor: Colors.redAccent),
        );
        ref.read(authProvider.notifier).clearError();
      }
    });

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Registro'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Colors.black87,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Icon(Icons.person_add_alt_1_rounded, size: 80, color: Colors.blueAccent),
                const SizedBox(height: 24),
                const Text(
                  'Crea una cuenta',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.black87),
                ),
                const SizedBox(height: 32),
                AuthInputField(label: 'Email (requerido)', icon: Icons.email_outlined, controller: _emailController),
                AuthInputField(label: 'Usuario (requerido)', icon: Icons.person_outline, controller: _usernameController),
                AuthInputField(label: 'Contraseña (requerido)', icon: Icons.lock_outline, isPassword: true, controller: _passwordController),
                AuthInputField(label: 'Nombre (opcional)', icon: Icons.badge_outlined, controller: _firstNameController),
                AuthInputField(label: 'Apellido (opcional)', icon: Icons.badge_outlined, controller: _lastNameController),
                AuthInputField(label: 'Departamento (opcional)', icon: Icons.business_outlined, controller: _departmentController),
                const SizedBox(height: 24),
                authState.status == AuthStatus.loading
                    ? const Center(child: CircularProgressIndicator())
                    : ElevatedButton(
                        onPressed: _handleRegister,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          backgroundColor: Colors.blueAccent,
                          foregroundColor: Colors.white,
                        ),
                        child: const Text('Registrarse', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('¿Ya tienes cuenta?'),
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Inicia Sesión', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
