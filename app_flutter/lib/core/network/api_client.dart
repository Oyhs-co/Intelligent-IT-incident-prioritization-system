import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiClient {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';

  Future<bool> enviarTicket(String title, String description) async {
    try {
      final url = Uri.parse('$baseUrl/incidents/');

      final respuesta = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'title': title,
          'description': description,

          'user_id': 1,
          'category': 'hardware',
        }),
      );

      if (respuesta.statusCode == 200 || respuesta.statusCode == 201) {
        debugPrint('¡Ticket enviado con éxito al servidor!');
        return true;
      } else {
        debugPrint('Error del servidor: ${respuesta.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('Fallo la conexion: $e');
      return false;
    }
  }
}
