import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_constants.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  final Logger _logger = Logger();

  String? _accessToken;
  String? _refreshToken;

  bool get isAuthenticated => _accessToken != null;

  String? get accessToken => _accessToken;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString(AppConstants.tokenKey);
    _refreshToken = prefs.getString(AppConstants.refreshTokenKey);
  }

  Future<void> setTokens({required String accessToken, required String refreshToken}) async {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.tokenKey, accessToken);
    await prefs.setString(AppConstants.refreshTokenKey, refreshToken);
  }

  Future<void> clearTokens() async {
    _accessToken = null;
    _refreshToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.tokenKey);
    await prefs.remove(AppConstants.refreshTokenKey);
    await prefs.remove(AppConstants.userKey);
  }

  Future<Map<String, String>> _headers({bool auth = false}) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    if (auth && _accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    return headers;
  }

  Future<dynamic> request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? queryParams,
    bool auth = false,
    Duration? timeout,
  }) async {
    final uri = Uri.parse('${AppConstants.baseUrl}$path').replace(queryParameters: queryParams);
    final headers = await _headers(auth: auth);
    final effectiveTimeout = timeout ?? AppConstants.requestTimeout;

    try {
      http.Response response;

      switch (method.toUpperCase()) {
        case 'GET':
          response = await http.get(uri, headers: headers).timeout(effectiveTimeout);
          break;
        case 'POST':
          response = await http.post(uri, headers: headers, body: body != null ? jsonEncode(body) : null).timeout(effectiveTimeout);
          break;
        case 'PUT':
          response = await http.put(uri, headers: headers, body: body != null ? jsonEncode(body) : null).timeout(effectiveTimeout);
          break;
        case 'PATCH':
          response = await http.patch(uri, headers: headers, body: body != null ? jsonEncode(body) : null).timeout(effectiveTimeout);
          break;
        case 'DELETE':
          response = await http.delete(uri, headers: headers).timeout(effectiveTimeout);
          break;
        default:
          throw ArgumentError('Unsupported HTTP method: $method');
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        if (response.body.isEmpty) return null;
        return jsonDecode(response.body);
      }

      if (response.statusCode == 401 && auth && _refreshToken != null) {
        final refreshed = await _tryRefresh();
        if (refreshed) {
          return request(method, path, body: body, queryParams: queryParams, auth: auth, timeout: timeout);
        }
      }

      final detail = _parseError(response.body);
      throw ApiException(response.statusCode, detail);
    } on ApiException {
      rethrow;
    } catch (e) {
      _logger.e('API request failed: $method $path — $e');
      rethrow;
    }
  }

  Future<bool> _tryRefresh() async {
    try {
      final uri = Uri.parse('${AppConstants.baseUrl}${ApiEndpoints.refresh}');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh_token': _refreshToken}),
      ).timeout(AppConstants.refreshTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await setTokens(
          accessToken: data['access_token'] as String,
          refreshToken: data['refresh_token'] as String,
        );
        return true;
      }
      await clearTokens();
      return false;
    } catch (e) {
      _logger.e('Token refresh failed: $e');
      await clearTokens();
      return false;
    }
  }

  String _parseError(String body) {
    try {
      final data = jsonDecode(body);
      if (data is Map && data.containsKey('detail')) {
        return data['detail'].toString();
      }
      return 'Unknown error';
    } catch (_) {
      return 'Unknown error';
    }
  }
}
