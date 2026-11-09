from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from . import models
from USErs.permissions import warnings

class OrderItemPermission(BasePermission):
    """
    Officiant ---- GET, POST
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        xizmetker = getattr(user, 'xizmetkerler', None)
        order_id = view.kwargs.get('pk')
        order = get_object_or_404(models.Order, id=order_id)

        if getattr(xizmetker, 'role', None)=='waiter':
            return xizmetker.restaurant == order.restaurant and xizmetker == order.waiter
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        xizmetker = getattr(user, 'xizmetkerler', None)
        return xizmetker == obj.waiter
    
    




class OrderItemUpdatePermision(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        xizmetker = getattr(user, "xizmetkerler", None)
        return bool(
            xizmetker
            and xizmetker.is_active
            and xizmetker.role == "waiter"
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        xizmetker = getattr(user, "xizmetkerler", None)

        if not xizmetker or not xizmetker.is_active:
            return False

        # 1. Restoran mosligi tekshiruv
        if obj.order.restaurant != xizmetker.restaurant:
            return False

        # 2. O'zgartirish (PUT, PATCH, DELETE) faqat 'J' (Jana) statusida ruxsat beriladi
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.status == "new"

        return True


class OrderItemWaiterUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user and not user.is_authenticated:
            return False 
        xizmetker = getattr(user, 'xizmetkerler', None)
        admin = getattr(user, 'adminler', None)
        if xizmetker and getattr(xizmetker, 'role', None)=='waiter':
            if not getattr(xizmetker, 'is_active', True):
                self.message=warnings[1]
                return False
            return True

        if admin:
            if not getattr(admin, 'is_active', True):
                self.message = warnings[0]
                return False
            return True
    
        return False


    def has_object_permission(self, request, view, obj):
        user = request.user
        xizmetker = getattr(user, 'xizmetkerler', None)
        admin = getattr(user, 'adminler', None)

        if admin:
            return admin.restaurant == obj.order.restaurant
        if xizmetker:
            return xizmetker.restaurant == obj.order.restaurant
        
        if request.method == 'PATCH':
            return obj.status == 'ready'

        return False
    
class IsKitchenStaffPermission(BasePermission):
  

    def has_permission(self, request, view):
        user = request.user
        admin = getattr(user, 'adminler', None)
        xizmetker = getattr(user, "xizmetkerler", None)
        if xizmetker and xizmetker.is_active:
            return xizmetker.role == "cook"

        if admin and admin.is_active:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        xizmetker = getattr(user, "xizmetkerler", None)
        admin = getattr(user, 'adminler', None)
        if xizmetker:
            return xizmetker.restaurant == obj.order.restaurant
        if admin:
            return admin.restaurant == obj.order.restaurant
        return False