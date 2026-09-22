from rest_framework.permissions import BasePermission
from restaurant.permissions import warnings


class IsCustomerOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'customers')

    def has_object_permission(self, request, view, obj):
        # eger obj Reservation bolsa
        if hasattr(obj, 'client'):
            return obj.client.user == request.user 

        # obj bu jerde Customer modeli
        return obj.id == request.user.customers.id


class IsRestoranAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restoran'):
            if not user.adminler.is_active:
                self.message = warnings[0]
                return False
            
            return view.kwargs['pk'] == admin.restoran.id
        
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(user, 'adminler'):
            if not user.adminler.is_active:
                self.message = warnings[0]
                return False
            
            if hasattr(obj, 'restoran'):
                return obj.restoran.id == user.adminler.restoran.id
            return False
        return False




class XizmetkerDetailPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        admin = getattr(user,'adminler', None)
        if admin:
            if not getattr(admin, 'is_active', True):
                self.message = "Siz aktiv emessiz. Super Adminge muraja etin!"
                return False

            if getattr(admin, 'restoran', None):
                return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        admin = getattr(user, 'adminler', None)

        if admin and getattr(admin, 'restoran', None):
            if not getattr(admin, 'is_active', True):
                self.message = "Siz aktiv emessiz. Super Adminge muraja etin!"
                return False
            
            if hasattr(obj, 'restoran'):
                return obj.restoran == admin.restoran
            return False

    
        