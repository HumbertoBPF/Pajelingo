from rest_framework import permissions


class AllowPostOnly(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        # Allow only post requests
        if request.method == 'POST':
            return True

        return super().has_permission(request, view)