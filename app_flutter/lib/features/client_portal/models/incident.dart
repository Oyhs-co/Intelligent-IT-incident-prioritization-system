// Modelo basico de incidente.
class Incident {
  final String id;
  final String title;
  final String description;
  final String status;

  // Datos requeridos para crear un incidente.
  Incident({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
  });
}
