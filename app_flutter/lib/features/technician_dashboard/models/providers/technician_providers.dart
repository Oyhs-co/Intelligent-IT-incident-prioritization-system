import 'package:flutter_riverpod/flutter_riverpod.dart';

class TechnicianFilterNotifier extends Notifier<String> {
  @override
  String build() => 'Todos';

  void setFilter(String filter) {
    state = filter;
  }
}

final technicianFilterProvider = NotifierProvider<TechnicianFilterNotifier, String>(TechnicianFilterNotifier.new);
