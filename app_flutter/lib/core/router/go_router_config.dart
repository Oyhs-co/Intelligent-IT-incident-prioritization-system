import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/register_page.dart';
import '../../features/client_portal/presentation/pages/client_home.dart';
import '../../features/client_portal/presentation/pages/new_report.dart';
import '../../features/client_portal/presentation/pages/incident_details.dart';
import '../../features/client_portal/presentation/pages/client_profile_page.dart';
import '../../features/analyst_dashboard/presentation/pages/dashboard_page.dart';
import '../../features/analyst_dashboard/presentation/pages/incident_review_page.dart';
import '../../features/analyst_dashboard/presentation/pages/analyst_history_page.dart';
import '../../features/analyst_dashboard/presentation/pages/analyst_metrics_page.dart';
import '../../features/analyst_dashboard/presentation/pages/analyst_settings_page.dart';
import '../../features/analyst_dashboard/presentation/pages/analyst_directory_page.dart';
import '../../features/technician_dashboard/presentation/pages/technician_dashboard_page.dart';
import '../../features/technician_dashboard/presentation/pages/technician_resolve_page.dart';
import '../../features/admin/presentation/pages/admin_dashboard_page.dart';
import '../../features/admin/presentation/pages/global_tickets_page.dart';
import '../../features/admin/presentation/pages/user_management_page.dart';
import '../../features/admin/presentation/pages/ai_settings_page.dart';
import '../../features/admin/presentation/pages/admin_ticket_audit_page.dart';
import '../../features/client_portal/models/incident.dart';
import '../../features/auth/providers/auth_providers.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/login',
    redirect: (context, state) {
      final role = authState.user?.role ?? 'user';
      return resolveRedirect(
        isLoggedIn: authState.isAuthenticated,
        location: state.matchedLocation,
        role: role,
      );
    },
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (context, state) => const RegisterPage(),
      ),
      GoRoute(
        path: '/client/home',
        name: 'clientHome',
        builder: (context, state) => const ClientHome(),
      ),
      GoRoute(
        path: '/client/new-report',
        name: 'newReport',
        builder: (context, state) => const NewReportPage(),
      ),
      GoRoute(
        path: '/client/incident/:id',
        name: 'incidentDetails',
        builder: (context, state) {
          final incident = state.extra as Incident;
          return IncidentDetailsPage(incident: incident);
        },
      ),
      GoRoute(
        path: '/client/profile',
        name: 'clientProfile',
        builder: (context, state) => const ClientProfilePage(),
      ),
      GoRoute(
        path: '/technician/dashboard',
        name: 'technicianDashboard',
        builder: (context, state) => const TechnicianDashboardPage(),
      ),
      GoRoute(
        path: '/technician/resolve/:id',
        name: 'technicianResolve',
        builder: (context, state) {
          final ticket = state.extra as Incident;
          return TechnicianResolvePage(ticket: ticket);
        },
      ),
      GoRoute(
        path: '/analyst/dashboard',
        name: 'analystDashboard',
        builder: (context, state) => const AnalystDashboardPage(),
      ),
      GoRoute(
        path: '/analyst/incident/:id',
        name: 'analystIncidentReview',
        builder: (context, state) {
          final ticket = state.extra as Incident;
          return IncidentReviewPage(ticket: ticket);
        },
      ),
      GoRoute(
        path: '/analyst/history',
        name: 'analystHistory',
        builder: (context, state) => const AnalystHistoryPage(),
      ),
      GoRoute(
        path: '/analyst/metrics',
        name: 'analystMetrics',
        builder: (context, state) => const AnalystMetricsPage(),
      ),
      GoRoute(
        path: '/analyst/settings',
        name: 'analystSettings',
        builder: (context, state) => const AnalystSettingsPage(),
      ),
      GoRoute(
        path: '/analyst/directory',
        name: 'analystDirectory',
        builder: (context, state) => const AnalystDirectoryPage(),
      ),
      GoRoute(
        path: '/admin/dashboard',
        name: 'adminDashboard',
        builder: (context, state) => const AdminDashboardPage(),
      ),
      GoRoute(
        path: '/admin/tickets',
        name: 'adminTickets',
        builder: (context, state) => const GlobalTicketsPage(),
      ),
      GoRoute(
        path: '/admin/users',
        name: 'adminUsers',
        builder: (context, state) => const UserManagementPage(),
      ),
      GoRoute(
        path: '/admin/ai-settings',
        name: 'adminAISettings',
        builder: (context, state) => const AISettingsPage(),
      ),
      GoRoute(
        path: '/admin/ticket-audit/:id',
        name: 'adminTicketAudit',
        builder: (context, state) {
          final ticket = state.extra as Incident;
          return AdminTicketAuditPage(ticket: ticket);
        },
      ),
    ],
  );
});

@visibleForTesting
String? resolveRedirect({
  required bool isLoggedIn,
  required String location,
  required String role,
}) {
  final isLoginRoute = location == '/login';
  final isRegisterRoute = location == '/register';

  if (!isLoggedIn && !isLoginRoute && !isRegisterRoute) {
    return '/login';
  }

  if (isLoggedIn && (isLoginRoute || isRegisterRoute)) {
    return _getHomeRoute(role);
  }

  if (isLoggedIn && !_isRouteAllowedForRole(location, role)) {
    return _getHomeRoute(role);
  }

  return null;
}

@visibleForTesting
bool isRouteAllowedForRole(String location, String role) {
  return _isRouteAllowedForRole(location, role);
}

@visibleForTesting
String getHomeRouteForRole(String role) {
  return _getHomeRoute(role);
}

bool _isRouteAllowedForRole(String location, String role) {
  if (location == '/login' || location == '/register') return true;

  switch (role) {
    case 'admin':
      return location.startsWith('/admin/');
    case 'technician':
      return location.startsWith('/technician/');
    case 'analyst':
      return location.startsWith('/analyst/');
    case 'user':
      return location.startsWith('/client/');
    default:
      return false;
  }
}

String _getHomeRoute(String role) {
  switch (role) {
    case 'admin':
      return '/admin/dashboard';
    case 'technician':
      return '/technician/dashboard';
    case 'analyst':
      return '/analyst/dashboard';
    default:
      return '/client/home';
  }
}
