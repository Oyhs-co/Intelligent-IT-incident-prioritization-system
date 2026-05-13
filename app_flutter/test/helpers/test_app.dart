import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// ignore: implementation_imports
import 'package:riverpod/src/internals.dart' show Override;

Widget buildTestApp(
  Widget child, {
  List<Override> overrides = const <Override>[],
}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(home: Material(child: child)),
  );
}
