import 'package:flutter/material.dart';



class AppLogo extends StatelessWidget {
  const AppLogo({super.key, this.size = 72, this.showLabel = true});
  final double size;
  final bool showLabel;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF2563EB), Color(0xFF7C3AED)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(size * 0.26),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF2563EB).withValues(alpha: 0.40),
                  blurRadius: 28,
                  offset: const Offset(0, 12),
                ),
              ],
            ),
            child: Stack(
              alignment: Alignment.center,
              children: [
                // outer shield
                Icon(Icons.shield, color: Colors.white.withValues(alpha: 0.15), size: size * 0.72),
                // lightning bolt
                Icon(Icons.bolt, color: Colors.white, size: size * 0.46),
              ],
            ),
          ),
          if (showLabel) ...[
            const SizedBox(height: 12),
            
            RichText(
              text: TextSpan(
                children: [
                  TextSpan(
                    text: 'SIPII',
                    style: TextStyle(
                      fontSize: size * 0.28,
                      fontWeight: FontWeight.w900,
                      color: cs.onSurface,
                      letterSpacing: 2,
                    ),
                  ),
                  TextSpan(
                    text: 'T',
                    style: TextStyle(
                      fontSize: size * 0.28,
                      fontWeight: FontWeight.w900,
                      foreground: Paint()
                        ..shader = const LinearGradient(
                          colors: [Color(0xFF2563EB), Color(0xFF7C3AED)],
                        ).createShader(Rect.fromLTWH(0, 0, 40, 40)),
                      letterSpacing: 2,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 3),
            Text(
              'Sistema de Priorización de Incidentes',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: size * 0.11,
                color: cs.onSurfaceVariant,
                letterSpacing: 0.3,
              ),
            ),
          ],
        ],
      ),
    );
  }
}




class AuthBrandHeader extends StatelessWidget {
  const AuthBrandHeader({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Column(
      children: [
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [cs.primary, const Color(0xFF7C3AED)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: cs.primary.withValues(alpha: 0.3),
                blurRadius: 18,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Icon(icon, color: Colors.white, size: 28),
        ),
        const SizedBox(height: 16),
        Text(
          title,
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w800,
            color: cs.onSurface,
            letterSpacing: -0.5,
          ),
        ),
        const SizedBox(height: 5),
        Text(
          subtitle,
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 13, color: cs.onSurfaceVariant),
        ),
      ],
    );
  }
}


class AuthFormCard extends StatelessWidget {
  const AuthFormCard({super.key, required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.7)),
        boxShadow: [
          BoxShadow(
            color: cs.shadow.withValues(alpha: 0.07),
            blurRadius: 20,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: child,
    );
  }
}



class AuthPrimaryButton extends StatelessWidget {
  const AuthPrimaryButton({
    super.key,
    required this.label,
    required this.icon,
    required this.isLoading,
    required this.onPressed,
  });

  final String label;
  final IconData icon;
  final bool isLoading;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    if (isLoading) {
      return Container(
        height: 50,
        decoration: BoxDecoration(
          color: cs.primary.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: SizedBox(
            width: 22, height: 22,
            child: CircularProgressIndicator(strokeWidth: 2.5, color: cs.primary),
          ),
        ),
      );
    }

    return FilledButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 18),
      label: Text(label),
    );
  }
}



class AuthFooterLink extends StatelessWidget {
  const AuthFooterLink({
    super.key,
    required this.question,
    required this.actionLabel,
    required this.onTap,
  });

  final String question;
  final String actionLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(question, style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13)),
        TextButton(
          onPressed: onTap,
          style: TextButton.styleFrom(
            foregroundColor: cs.primary,
            padding: const EdgeInsets.symmetric(horizontal: 6),
            textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
          ),
          child: Text(actionLabel),
        ),
      ],
    );
  }
}



class AuthSectionLabel extends StatelessWidget {
  const AuthSectionLabel({super.key, required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Text(
      label.toUpperCase(),
      style: TextStyle(
        color: cs.primary,
        fontSize: 10,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.2,
      ),
    );
  }
}
