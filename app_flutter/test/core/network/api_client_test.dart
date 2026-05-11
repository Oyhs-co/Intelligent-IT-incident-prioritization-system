import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:app_flutter/core/network/api_client.dart';
import 'package:app_flutter/core/utils/app_constants.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    await ApiClient().clearTokens();
  });

  test('setTokens persists tokens and updates auth state', () async {
    final api = ApiClient();
    await api.init();

    expect(api.isAuthenticated, isFalse);

    await api.setTokens(accessToken: 'access', refreshToken: 'refresh');

    expect(api.isAuthenticated, isTrue);

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString(AppConstants.tokenKey), 'access');
    expect(prefs.getString(AppConstants.refreshTokenKey), 'refresh');
  });

  test('clearTokens removes stored tokens', () async {
    final api = ApiClient();
    await api.setTokens(accessToken: 'a', refreshToken: 'b');

    await api.clearTokens();

    expect(api.isAuthenticated, isFalse);

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString(AppConstants.tokenKey), isNull);
    expect(prefs.getString(AppConstants.refreshTokenKey), isNull);
  });
}
