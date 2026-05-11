import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';


class ThemeModeNotifier extends Notifier<ThemeMode> {
  @override
  ThemeMode build() => ThemeMode.system;

  void setLight()  => state = ThemeMode.light;
  void setDark()   => state = ThemeMode.dark;
  void setSystem() => state = ThemeMode.system;

  void toggle() {
    state = state == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
  }

  bool get isDark => state == ThemeMode.dark;
}

final themeModeProvider =
    NotifierProvider<ThemeModeNotifier, ThemeMode>(ThemeModeNotifier.new);
