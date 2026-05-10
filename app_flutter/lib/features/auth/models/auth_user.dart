class AuthUser {
  final String id;
  final String email;
  final String username;
  final String role;
  final String? firstName;
  final String? lastName;
  final String? fullName;
  final String? department;
  final bool isActive;
  final bool isVerified;
  final String? lastLogin;
  final String createdAt;

  AuthUser({
    required this.id,
    required this.email,
    required this.username,
    required this.role,
    this.firstName,
    this.lastName,
    this.fullName,
    this.department,
    required this.isActive,
    required this.isVerified,
    this.lastLogin,
    required this.createdAt,
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] as String,
      email: json['email'] as String,
      username: json['username'] as String,
      role: json['role'] as String,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      fullName: json['full_name'] as String?,
      department: json['department'] as String?,
      isActive: json['is_active'] as bool,
      isVerified: json['is_verified'] as bool,
      lastLogin: json['last_login'] as String?,
      createdAt: json['created_at'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'role': role,
      'first_name': firstName,
      'last_name': lastName,
      'full_name': fullName,
      'department': department,
      'is_active': isActive,
      'is_verified': isVerified,
      'last_login': lastLogin,
      'created_at': createdAt,
    };
  }
}
