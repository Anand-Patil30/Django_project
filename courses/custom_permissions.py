from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

class StudentRolePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'student'
        else:
            return False

class TeacherRolePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'teacher'
        else:
            return False

class IsCourseOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user