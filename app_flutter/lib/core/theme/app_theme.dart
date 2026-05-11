import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  
  static const Color _seed        = Color(0xFF2563EB); 
  static const Color _teal        = Color(0xFF0D9488); 
  static const Color _violet      = Color(0xFF7C3AED); 
  static const Color _amber       = Color(0xFFD97706); 
  static const Color _emerald     = Color(0xFF059669); 

  
  static Color get roleAdmin      => _violet;
  static Color get roleAnalyst    => _seed;
  static Color get roleTechnician => _emerald;
  static Color get roleClient     => _amber;
  static Color get roleTeal       => _teal;

  
  static ThemeData get lightTheme {
    final cs = ColorScheme.fromSeed(
      seedColor: _seed,
      brightness: Brightness.light,
      surface: const Color(0xFFFFFFFF),
      surfaceContainerLowest: const Color(0xFFF1F5F9),
      surfaceContainerHighest: const Color(0xFFE2E8F0),
      onSurface: const Color(0xFF0F172A),
      onSurfaceVariant: const Color(0xFF475569),
      outline: const Color(0xFFCBD5E1),
      outlineVariant: const Color(0xFFE2E8F0),
    );

    return _buildTheme(cs);
  }

  
  static ThemeData get darkTheme {
    final cs = ColorScheme.fromSeed(
      seedColor: _seed,
      brightness: Brightness.dark,
      surface: const Color(0xFF1E293B),
      surfaceContainerLowest: const Color(0xFF0F172A),
      surfaceContainerHighest: const Color(0xFF334155),
      onSurface: const Color(0xFFF1F5F9),
      onSurfaceVariant: const Color(0xFF94A3B8),
      outline: const Color(0xFF475569),
      outlineVariant: const Color(0xFF334155),
    );

    return _buildTheme(cs);
  }

  static ThemeData _buildTheme(ColorScheme cs) {
    final base = ThemeData(useMaterial3: true, colorScheme: cs);

    return base.copyWith(
      scaffoldBackgroundColor: cs.surfaceContainerLowest,
      textTheme: GoogleFonts.interTextTheme(base.textTheme).copyWith(
        displayLarge:  GoogleFonts.inter(fontWeight: FontWeight.w800, fontSize: 32, letterSpacing: -1.0, color: cs.onSurface),
        displayMedium: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 26, letterSpacing: -0.6, color: cs.onSurface),
        titleLarge:    GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 18, letterSpacing: -0.3, color: cs.onSurface),
        titleMedium:   GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 15, color: cs.onSurface),
        bodyLarge:     GoogleFonts.inter(fontSize: 15, color: cs.onSurface, height: 1.5),
        bodyMedium:    GoogleFonts.inter(fontSize: 13, color: cs.onSurfaceVariant, height: 1.4),
        labelLarge:    GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0.5,
        centerTitle: false,
        backgroundColor: cs.surface,
        foregroundColor: cs.onSurface,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 17,
          fontWeight: FontWeight.w700,
          color: cs.onSurface,
          letterSpacing: -0.3,
        ),
        iconTheme: IconThemeData(color: cs.onSurfaceVariant, size: 22),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: cs.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.7)),
        ),
        margin: const EdgeInsets.only(bottom: 10),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: cs.surfaceContainerHighest.withValues(alpha: 0.5),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        labelStyle: TextStyle(color: cs.onSurfaceVariant, fontSize: 13),
        hintStyle: TextStyle(color: cs.onSurfaceVariant.withValues(alpha: 0.6), fontSize: 13),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cs.outlineVariant),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cs.outlineVariant),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cs.primary, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cs.error, width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: cs.error, width: 2),
        ),
        errorStyle: TextStyle(color: cs.error, fontSize: 11, fontWeight: FontWeight.w500),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: cs.primary,
          foregroundColor: cs.onPrimary,
          elevation: 0,
          padding: const EdgeInsets.symmetric(vertical: 16),
          textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(double.infinity, 50),
          textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: cs.primary,
        foregroundColor: cs.onPrimary,
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        side: BorderSide.none,
      ),
      dividerTheme: DividerThemeData(color: cs.outlineVariant, thickness: 1),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}
