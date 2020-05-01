from rest_framework.permissions import BasePermission, IsAuthenticated as BaseIsAuthenticated


class CustomPermission(BasePermission):

    def call_from_swagger(self, request):
        return request.META['PATH_INFO'] == '/swagger/'


class IsAuthenticated(BaseIsAuthenticated, CustomPermission):

    def has_permission(self, request, view):
        if self.call_from_swagger(request):
            return True

        return super(IsAuthenticated, self).has_permission(request, view)
