import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/auth_providers.dart';
import '../widgets/auth_input_field.dart';
import '../widgets/auth_shared_widgets.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _emailController      = TextEditingController();
  final _usernameController   = TextEditingController();
  final _passwordController   = TextEditingController();
  final _firstNameController  = TextEditingController();
  final _lastNameController   = TextEditingController();
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
    final email    = _emailController.text.trim();
    final username = _usernameController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || username.isEmpty || password.isEmpty) {
      _showSnack('Email, usuario y contraseña son requeridos');
      return;
    }

    ref.read(authProvider.notifier).register(
      email:      email,
      username:   username,
      password:   password,
      firstName:  _firstNameController.text.trim(),
      lastName:   _lastNameController.text.trim(),
      department: _departmentController.text.trim(),
    );
  }

  void _showSnack(String msg, {bool isError = true}) {
    final cs = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(children: [
          Icon(
            isError ? Icons.error_outline : Icons.check_circle_outline,
            color: isError ? cs.onError : cs.onPrimary,
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(child: Text(msg, style: const TextStyle(fontSize: 13))),
        ]),
        backgroundColor: isError ? cs.error : cs.primary,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final cs        = Theme.of(context).colorScheme;
    final isLoading = authState.status == AuthStatus.loading;

    ref.listen(authProvider, (previous, next) {
      if (next.error != null) {
        _showSnack(next.error!);
        ref.read(authProvider.notifier).clearError();
      }
    });

    return Scaffold(
      backgroundColor: cs.surfaceContainerLowest,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_new_outlined,
              size: 18, color: cs.onSurfaceVariant),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(28, 0, 28, 40),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // ── Brand header ──────────────────────────────────
                  const AuthBrandHeader(
                    icon: Icons.person_add_outlined,
                    title: 'Crear cuenta',
                    subtitle: 'Completa tu información para registrarte',
                  ),
                  const SizedBox(height: 32),

                  // ── Form card ─────────────────────────────────────
                  AuthFormCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Sección: acceso
                        const AuthSectionLabel(label: 'Información de acceso'),
                        const SizedBox(height: 12),
                        AuthInputField(
                          label: 'Correo electrónico',
                          icon: Icons.alternate_email,
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                        ),
                        AuthInputField(
                          label: 'Nombre de usuario',
                          icon: Icons.account_circle_outlined,
                          controller: _usernameController,
                        ),
                        AuthInputField(
                          label: 'Contraseña',
                          icon: Icons.lock_outline,
                          isPassword: true,
                          controller: _passwordController,
                        ),

                        // Divider con etiqueta
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          child: Row(children: [
                            Expanded(
                                child: Divider(
                                    color: cs.outlineVariant, thickness: 1)),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 12),
                              child: Text(
                                'Información personal',
                                style: TextStyle(
                                  color: cs.onSurfaceVariant,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                            Expanded(
                                child: Divider(
                                    color: cs.outlineVariant, thickness: 1)),
                          ]),
                        ),
                        const SizedBox(height: 4),

                        // Nombre y apellido en fila
                        Row(
                          children: [
                            Expanded(
                              child: AuthInputField(
                                label: 'Nombre',
                                icon: Icons.badge_outlined,
                                controller: _firstNameController,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: AuthInputField(
                                label: 'Apellido',
                                icon: Icons.badge_outlined,
                                controller: _lastNameController,
                              ),
                            ),
                          ],
                        ),
                        AuthInputField(
                          label: 'Departamento (opcional)',
                          icon: Icons.corporate_fare_outlined,
                          controller: _departmentController,
                        ),

                        const SizedBox(height: 8),
                        AuthPrimaryButton(
                          label: 'Crear Cuenta',
                          icon: Icons.person_add_outlined,
                          isLoading: isLoading,
                          onPressed: _handleRegister,
                        ),
                      ],
                    ),
                  ),

                  // ── Footer link ───────────────────────────────────
                  const SizedBox(height: 24),
                  AuthFooterLink(
                    question: '¿Ya tienes una cuenta?',
                    actionLabel: 'Inicia Sesión',
                    onTap: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
