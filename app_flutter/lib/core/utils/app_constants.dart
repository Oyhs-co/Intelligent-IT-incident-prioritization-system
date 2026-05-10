class AppConstants {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  static const Duration requestTimeout = Duration(seconds: 10);
  static const Duration refreshTimeout = Duration(seconds: 5);

  static const String tokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'current_user';

  static const int accessTokenExpiry = 1800;
  static const int refreshTokenExpiry = 604800;
}

class ApiEndpoints {
  static const String incidents = '/incidents/';
  static String incident(String id) => '/incidents/$id';
  static String classifyIncident(String id) => '/incidents/$id/classify';
  static String updateIncident(String id) => '/incidents/$id';

  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String refresh = '/auth/refresh';
  static const String me = '/auth/me';

  static const String metricsOverview = '/metrics/overview';
  static const String metricsIncidents = '/metrics/incidents';
  static const String metricsAI = '/metrics/ai';
  static const String metricsHealth = '/metrics/health';
}
