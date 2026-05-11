import 'package:flutter/material.dart';

class AuthInputField extends StatefulWidget {
  final String label;
  final IconData icon;
  final bool isPassword;
  final TextEditingController? controller;
  final TextInputType? keyboardType;
  final String? Function(String?)? validator;
  final String? hintText;

  const AuthInputField({
    super.key,
    required this.label,
    required this.icon,
    this.isPassword = false,
    this.controller,
    this.keyboardType,
    this.validator,
    this.hintText,
  });

  @override
  State<AuthInputField> createState() => _AuthInputFieldState();
}

class _AuthInputFieldState extends State<AuthInputField> {
  bool _obscure = true;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: TextFormField(
        controller: widget.controller,
        obscureText: widget.isPassword && _obscure,
        keyboardType: widget.keyboardType,
        validator: widget.validator,
        autovalidateMode: AutovalidateMode.onUserInteraction,
        style: TextStyle(color: cs.onSurface, fontSize: 14),
        decoration: InputDecoration(
          labelText: widget.label,
          hintText: widget.hintText,
          prefixIcon: Icon(widget.icon, size: 18, color: cs.onSurfaceVariant),
          suffixIcon: widget.isPassword
              ? IconButton(
                  icon: Icon(
                    _obscure
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                    size: 18,
                    color: cs.onSurfaceVariant,
                  ),
                  onPressed: () => setState(() => _obscure = !_obscure),
                )
              : null,
        ),
      ),
    );
  }
}
