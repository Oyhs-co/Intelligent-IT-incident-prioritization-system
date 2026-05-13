import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_providers.dart';
import '../widgets/auth_input_field.dart';
import '../widgets/auth_shared_widgets.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _formKey             = GlobalKey<FormState>();
  final _emailCtrl           = TextEditingController();
  final _usernameCtrl        = TextEditingController();
  final _passwordCtrl        = TextEditingController();
  final _firstNameCtrl       = TextEditingController();
  final _lastNameCtrl        = TextEditingController();
  final _departmentCtrl      = TextEditingController();

  @override
  void dispose() {
    _emailCtrl.dispose();
    _usernameCtrl.dispose();
    _passwordCtrl.dispose();
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _departmentCtrl.dispose();
    super.dispose();
  }

 

  String? _validateEmail(String? v) {
    if (v == null || v.trim().isEmpty) return 'El correo es requerido';
    final regex = RegExp(r'^[\w\.\-]+@[\w\-]+\.\w{2,}$');
    if (!regex.hasMatch(v.trim())) return 'Ingresa un correo válido';
    return null;
  }

  String? _validateUsername(String? v) {
    if (v == null || v.trim().isEmpty) return 'El nombre de usuario es requerido';
    if (v.trim().length < 3) return 'Mínimo 3 caracteres';
    if (!RegExp(r'^[\w\.\-]+$').hasMatch(v.trim())) return 'Solo letras, números, puntos o guiones';
    return null;
  }

  String? _validatePassword(String? v) {
    if (v == null || v.isEmpty) return 'La contraseña es requerida';
    if (v.length < 8) return 'Mínimo 8 caracteres';
    if (!RegExp(r'[A-Z]').hasMatch(v)) return 'Debe contener al menos una mayúscula';
    if (!RegExp(r'[0-9]').hasMatch(v)) return 'Debe contener al menos un número';
    return null;
  }

  String? _validateRequired(String? v, String field) {
    if (v == null || v.trim().isEmpty) return '$field es requerido';
    return null;
  }

  

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    ref.read(authProvider.notifier).register(
      email:      _emailCtrl.text.trim(),
      username:   _usernameCtrl.text.trim(),
      password:   _passwordCtrl.text,
      firstName:  _firstNameCtrl.text.trim(),
      lastName:   _lastNameCtrl.text.trim(),
      department: _departmentCtrl.text.trim(),
    );
  }

  void _showSnack(String msg, {bool isError = true}) {
    final cs = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(children: [
          Icon(
            isError ? Icons.error_outline : Icons.check_circle_outline,
            color: Colors.white, size: 18,
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
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_new_outlined, size: 18, color: cs.onSurfaceVariant),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(28, 0, 28, 40),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const AuthBrandHeader(
                      icon: Icons.person_add_outlined,
                      title: 'Crear cuenta',
                      subtitle: 'Completa tu información para registrarte',
                    ),
                    const SizedBox(height: 28),

                    AuthFormCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                         
                          const AuthSectionLabel(label: 'Información de acceso'),
                          const SizedBox(height: 14),
                          AuthInputField(
                            label: 'Correo electrónico',
                            icon: Icons.alternate_email,
                            controller: _emailCtrl,
                            keyboardType: TextInputType.emailAddress,
                            validator: _validateEmail,
                          ),
                          AuthInputField(
                            label: 'Nombre de usuario',
                            icon: Icons.account_circle_outlined,
                            controller: _usernameCtrl,
                            validator: _validateUsername,
                            hintText: 'Sin espacios ni caracteres especiales',
                          ),
                          AuthInputField(
                            label: 'Contraseña',
                            icon: Icons.lock_outline,
                            isPassword: true,
                            controller: _passwordCtrl,
                            validator: _validatePassword,
                            hintText: '8+ caracteres, 1 mayúscula, 1 número',
                          ),

                          
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 10),
                            child: Row(children: [
                              Expanded(child: Divider(color: cs.outlineVariant)),
                              Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 12),
                                child: Text('Información personal',
                                    style: TextStyle(
                                        color: cs.onSurfaceVariant, fontSize: 11, fontWeight: FontWeight.w500)),
                              ),
                              Expanded(child: Divider(color: cs.outlineVariant)),
                            ]),
                          ),

                         
                          Row(
                            children: [
                              Expanded(
                                child: AuthInputField(
                                  label: 'Nombre',
                                  icon: Icons.badge_outlined,
                                  controller: _firstNameCtrl,
                                  validator: (v) => _validateRequired(v, 'Nombre'),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: AuthInputField(
                                  label: 'Apellido',
                                  icon: Icons.badge_outlined,
                                  controller: _lastNameCtrl,
                                  validator: (v) => _validateRequired(v, 'Apellido'),
                                ),
                              ),
                            ],
                          ),
                          AuthInputField(
                            label: 'Departamento (opcional)',
                            icon: Icons.corporate_fare_outlined,
                            controller: _departmentCtrl,
                          ),

                          
                          _PasswordStrengthBar(controller: _passwordCtrl),
                          const SizedBox(height: 16),

                          AuthPrimaryButton(
                            label: 'Crear Cuenta',
                            icon: Icons.person_add_outlined,
                            isLoading: isLoading,
                            onPressed: _handleRegister,
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 24),
                    AuthFooterLink(
                      question: '¿Ya tienes una cuenta?',
                      actionLabel: 'Inicia Sesión',
                      onTap: () => context.pop(),
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



class _PasswordStrengthBar extends StatefulWidget {
  const _PasswordStrengthBar({required this.controller});
  final TextEditingController controller;

  @override
  State<_PasswordStrengthBar> createState() => _PasswordStrengthBarState();
}

class _PasswordStrengthBarState extends State<_PasswordStrengthBar> {
  @override
  void initState() {
    super.initState();
    widget.controller.addListener(() => setState(() {}));
  }

  int get _strength {
    final p = widget.controller.text;
    if (p.isEmpty) return 0;
    int score = 0;
    if (p.length >= 8) score++;
    if (RegExp(r'[A-Z]').hasMatch(p)) score++;
    if (RegExp(r'[0-9]').hasMatch(p)) score++;
    if (RegExp(r'[!@#\$%^&*]').hasMatch(p)) score++;
    return score;
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    if (widget.controller.text.isEmpty) return const SizedBox.shrink();

    final s = _strength;
    final labels = ['', 'Débil', 'Regular', 'Buena', 'Fuerte'];
    final colors = [Colors.transparent, cs.error, const Color(0xFFD97706), const Color(0xFF2563EB), const Color(0xFF059669)];

    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: List.generate(4, (i) => Expanded(
              child: Container(
                margin: const EdgeInsets.only(right: 4),
                height: 4,
                decoration: BoxDecoration(
                  color: i < s ? colors[s] : cs.outlineVariant,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            )),
          ),
          const SizedBox(height: 4),
          Text(
            s > 0 ? 'Contraseña: ${labels[s]}' : '',
            style: TextStyle(fontSize: 11, color: s > 0 ? colors[s] : cs.onSurfaceVariant, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}
