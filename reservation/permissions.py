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


        waiter = getattr(user, 'xizmetkerler', None)
        if waiter:
            if not getattr(waiter, 'is_active', None):
                self.message = warnings[1]
                return False

            return True
            
        return False



    def has_object_permission(self, request, view, obj):
        user = request.user

        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restaurant', None):
            return obj == admin.restaurant

        customer = getattr(user, 'customers', None)
        if customer:
            return True

        waiter = getattr(user, 'xizmetkerler', None)
        if waiter and getattr(waiter, 'restaurant', None):
            return obj == waiter.restaurant

        return False


class AdminReservation(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not(user and user.is_authenticated):
            return True

        admin = getattr(user, 'adminler', None)
        xizmetker = getattr(user, 'xizmetkerler', None)
        if admin:
            if not getattr(admin, 'is_active', True):
                self.message = warnings[0]
                return False
            return True

        if xizmetker:
            if not getattr(xizmetker, 'is_active', True):
                self.message = warnings[1]
                return False
            return request.method in permissions.SAFE_METHODS
        

        return False


    def has_object_permission(self, request, view, obj):
        user = request.user
        admin = getattr(user, 'adminler', None)
        xizmetker = getattr(user, 'xizmetkerler', None)
        if admin:
            return obj.restaurant == admin.restaurant
        if xizmetker:
            return obj.restaurant == xizmetker.restaurant
    