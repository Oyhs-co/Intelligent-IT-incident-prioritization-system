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
  final _formKey        = GlobalKey<FormState>();
  final _emailCtrl      = TextEditingController();
  final _passwordCtrl   = TextEditingController();

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  // ── validation ─────────────────────────────────────────────────────────────

  String? _validateEmail(String? v) {
    if (v == null || v.trim().isEmpty) return 'El correo es requerido';
    final regex = RegExp(r'^[\w\.\-]+@[\w\-]+\.\w{2,}$');
    if (!regex.hasMatch(v.trim())) return 'Ingresa un correo válido';
    return null;
  }

  String? _validatePassword(String? v) {
    if (v == null || v.isEmpty) return 'La contraseña es requerida';
    if (v.length < 6) return 'Mínimo 6 caracteres';
    return null;
  }

  void _handleLogin() {
    if (!_formKey.currentState!.validate()) return;
    ref.read(authProvider.notifier).login(
      _emailCtrl.text.trim(),
      _passwordCtrl.text,
    );
  }

  

  void _showSnack(String msg, {bool isError = true}) {
    final cs = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(children: [
          Icon(
            isError ? Icons.error_outline : Icons.check_circle_outline,
            color: Colors.white,
            size: 18,
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(msg, style: const TextStyle(fontSize: 13, color: Colors.white))),
        ]),
        backgroundColor: isError ? cs.error : const Color(0xFF059669),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

 

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final cs        = Theme.of(context).colorScheme;
    final isLoading = authState.status == AuthStatus.loading;

    ref.listen(authProvider, (_, next) {
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
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 32),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // ── Logo & Header ─────────────────────────────────
                    const AppLogo(size: 72),
                    const SizedBox(height: 24),
                    Text(
                      'Bienvenido',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.displayMedium,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Sistema de Priorización de Incidentes TI',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 36),

                    // ── Form card ─────────────────────────────────────
                    AuthFormCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          AuthInputField(
                            label: 'Correo electrónico',
                            icon: Icons.alternate_email,
                            controller: _emailCtrl,
                            keyboardType: TextInputType.emailAddress,
                            validator: _validateEmail,
                          ),
                          AuthInputField(
                            label: 'Contraseña',
                            icon: Icons.lock_outline,
                            isPassword: true,
                            controller: _passwordCtrl,
                            validator: _validatePassword,
                          ),
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton(
                              onPressed: () {},
                              style: TextButton.styleFrom(
                                foregroundColor: cs.primary,
                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
                                textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
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

                    
                    const SizedBox(height: 28),
                    const _RoleBadgeRow(),

                    
                    const SizedBox(height: 20),
                    AuthFooterLink(
                      question: '¿No tienes cuenta?',
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
      ),
    );
  }
}



class _RoleBadgeRow extends StatelessWidget {
  const _RoleBadgeRow();

  static const _roles = [
    _RoleInfo(Icons.person_outline,         'Cliente',      Color(0xFFD97706)),
    _RoleInfo(Icons.analytics_outlined,     'Analista',     Color(0xFF2563EB)),
    _RoleInfo(Icons.build_outlined,         'Técnico',      Color(0xFF059669)),
    _RoleInfo(Icons.admin_panel_settings_outlined, 'Admin', Color(0xFF7C3AED)),
  ];

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Column(
      children: [
        Text('Plataforma multi-rol', textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant,
                fontWeight: FontWeight.w500, letterSpacing: 0.5)),
        const SizedBox(height: 10),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: _roles.map((r) => _RolePill(info: r)).toList(),
        ),
      ],
    );
  }
}

class _RoleInfo {
  const _RoleInfo(this.icon, this.label, this.color);
  final IconData icon;
  final String label;
  final Color color;
}

class _RolePill extends StatelessWidget {
  const _RolePill({required this.info});
  final _RoleInfo info;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: info.color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: info.color.withValues(alpha: 0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(info.icon, size: 12, color: info.color),
            const SizedBox(width: 4),
            Text(info.label, style: TextStyle(fontSize: 10, color: info.color, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}
