import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/client_portal/presentation/pages/client_home.dart';

void main() {
  // Punto de entrada: inicializa Riverpod y arranca la app.
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SIPIIT',
      // Tema base de la aplicacion.
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      // Pantalla inicial del portal del cliente.
      home: const ClientHome(),
    );
  }
}
