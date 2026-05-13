import 'package:flutter_riverpod/flutter_riverpod.dart';

class AnalystFilterNotifier extends Notifier<String> {
  @override
  String build() => 'Todas';

  void setFilter(String filter) {
    state = filter;
  }
}

final analystFilterProvider = NotifierProvider<AnalystFilterNotifier, String>(AnalystFilterNotifier.new);
