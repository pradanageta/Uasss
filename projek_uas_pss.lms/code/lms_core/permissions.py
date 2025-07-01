from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    """
    Custom permission to only allow teachers to view or edit certain content.
    """
    def has_permission(self, request, view):
        # Pastikan user sudah login dan memiliki role 'teacher'
        return request.user.is_authenticated and request.user.profile.role == 'teacher'
    
class IsStudentOrTeacher(permissions.BasePermission):
    """
    Custom permission to allow both students and teachers to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsStudent(permissions.BasePermission):
    """
    Custom permission to only allow students to view or edit certain content.
    """
    def has_permission(self, request, view):
        # Pastikan user sudah login dan memiliki role 'student'
        return request.user.is_authenticated and request.user.profile.role == 'student'
