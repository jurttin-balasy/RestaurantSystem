from rest_framework.permissions import BasePermission, SAFE_METHODS
from restaurant.permissions import warnings
from django.shortcuts import get_object_or_404
from . import models


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

        if getattr(xizmetker, 'role', None)=='Officiant':
            return xizmetker.restoran == order.restoran and xizmetker == order.waiter
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
            and xizmetker.role == "Officiant"
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        xizmetker = getattr(user, "xizmetkerler", None)

        if not xizmetker or not xizmetker.is_active:
            return False

        # 1. Restoran mosligi tekshiruv
        if obj.order.restoran != xizmetker.restoran:
            return False

        # 2. O'zgartirish (PUT, PATCH, DELETE) faqat 'J' (Jana) statusida ruxsat beriladi
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.status == "J"

        return True



class IsKitchenStaffPermission(BasePermission):
    """KDS (Oshpazxona ekrani) uchun permission class.

    - Foydalanuvchi tizimdan o'tgan bo'lishi shart (IsAuthenticated).
    - Xodim faol (is_active=True) bo'lishi kerak.
    - Xodimning roli 'Oshpaz' (Povar) bo'lishi va restoranga biriktirilgan
    bo'lishi lozim.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        xizmetker = getattr(user, "xizmetkerler", None)
        if not xizmetker or not xizmetker.is_active:
            return False

        # Faqat Oshpaz rolidagi xodimlarga ruxsat beramiz
        return xizmetker.role == "Aspaz"

    def has_object_permission(self, request, view, obj):
        user = request.user
        xizmetker = getattr(user, "xizmetkerler", None)

        if not xizmetker or not xizmetker.is_active:
            return False

        # Oshpaz faqat o'zi ishlayotgan restorandagi taomlarni ko'ra oladi va statusini o'zgartiradi
        return obj.order.restoran == xizmetker.restoran    