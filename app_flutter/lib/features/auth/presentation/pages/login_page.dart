import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/auth_providers.dart';
import '../widgets/auth_input_field.dart';
import '../widgets/auth_shared_widgets.dart';
import 'register_page.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _emailController    = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _handleLogin() {
    final email    = _emailController.text.trim();
    final password = _passwordController.text.trim();
    if (email.isEmpty || password.isEmpty) {
      _showSnack('Email y contraseña requeridos');
      return;
    }
    ref.read(authProvider.notifier).login(email, password);
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
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 40),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const AuthBrandHeader(
                    icon: Icons.verified_user_outlined,
                    title: 'Bienvenido de nuevo',
                    subtitle: 'Inicia sesión en tu cuenta',
                  ),
                  const SizedBox(height: 36),

                  
                  AuthFormCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        AuthInputField(
                          label: 'Correo electrónico',
                          icon: Icons.alternate_email,
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                        ),
                        AuthInputField(
                          label: 'Contraseña',
                          icon: Icons.lock_outline,
                          isPassword: true,
                          controller: _passwordController,
                        ),
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () {},
                            style: TextButton.styleFrom(
                              foregroundColor: cs.primary,
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 4, vertical: 2),
                              textStyle: const TextStyle(
                                  fontSize: 12, fontWeight: FontWeight.w500),
                            ),
                            child: const Text('¿Olvidaste tu contraseña?'),
                          ),
                        ),
                        const SizedBox(height: 20),
                        AuthPrimaryButton(
                          label: 'Iniciar Sesión',
                          icon: Icons.login_outlined,
                          isLoading: isLoading,
                          onPressed: _handleLogin,
                        ),
                      ],
                    ),
                  ),

                 
                  const SizedBox(height: 24),
                  AuthFooterLink(
                    question: '¿No tienes una cuenta?',
                    actionLabel: 'Regístrate',
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const RegisterPage()),
                    ),
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
