from rest_framework import permissions
from USErs.permissions import warnings

class ReservationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        
        admin = getattr(user, 'adminler', None)
        if admin:
            if not getattr(admin, 'is_active', None):
                self.message = warnings[0]
                return False

            return request.method in permissions.SAFE_METHODS

        customer = getattr(user, 'customers', None)
        if customer:
            return True

        return False



    def has_object_permission(self, request, view, obj):
        user = request.user

        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restoran', None):
            return obj.restoran == admin.restoran

        customer = getattr(user, 'customers', None)
        if customer:
            return True

        return False


class AdminReservation(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not(user and user.is_authenticated):
            return True

        admin = getattr(user, 'adminler', None)
        if admin:
            if not getattr(admin, 'is_active', True):
                self.message = warnings[0]
                return False

            return True

        return False


    def has_object_permission(self, request, view, obj):
        user = request.user
        admin = getattr(user, 'adminler', None)
        return obj.restoran == admin.restoran

    