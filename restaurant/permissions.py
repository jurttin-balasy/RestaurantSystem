from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.shortcuts import get_object_or_404
from .models import Category, Dish


warnings = (
     "Siz aktiv emessiz. SuperAdminge xabarlasin",
     "Siz aktiv emessiz. Restoran adminge xabarlasin"
)


# restaurants/ AND restaurants/id/  
class SuperANDCustomer(BasePermission):
    """
    Superadmin -- GET POST
    Klient ----- GET
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if user.is_superuser:
            return True

        if hasattr(user, 'customers') and request.method in SAFE_METHODS:
            return True

        
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        if hasattr(user, 'customers') and request.method in SAFE_METHODS:
            return True

        return False


# restaurants/id/categories/  AND categories/id
class CategoryIngredientTableOrderListPermission(BasePermission):
    """
    Klient ushin ---- GET 
    Restoran admin ----- GET POST(restoran_id)
    Officiant ushin ------ GET (restoran_id)
    """


    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False


        # Faqat action `@action(detail=True, ...)` ya'ni `categories` bo'lgandagina 
        # Offitsiant va Adminlar o'tishi mumkin
        if getattr(view, 'action', None) == 'categories' or getattr(view, 'action', None) == 'tables':
            xizmetker = getattr(user, 'xizmetkerler', None)
            if xizmetker:
                if not getattr(xizmetker, 'is_active', True):
                    self.message = warnings[1]
                    return False
                
                return (getattr(xizmetker, 'role', None) == "Officiant" 
                and request.method in SAFE_METHODS)

            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', True):
                    self.message = warnings[0]
                    return False
                return bool(getattr(admin, 'restoran', None))

            customer = getattr(user, 'customers', None)
            if customer:
                return request.method in SAFE_METHODS



        if getattr(view, 'action', None) == 'ingredients':
            xizmetker = getattr(user, 'xizmetkerler', None)
            if xizmetker:
                if not getattr(xizmetker, 'is_active', True):
                    self.message = "Siz aktiv emessiz!"
                    return False

                return (getattr(xizmetker, 'role', None)=="Sklad xizmetkeri" 
                and request.method in SAFE_METHODS)

            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', None):
                    self.message = warnings[0]
                    return False
                return True
            

        if getattr(view, 'action', None) == 'orders':
            xizmetker = getattr(user, 'xizmetkerler', None)
            if xizmetker:
                if not getattr(xizmetker, 'is_active', True):
                    self.message = warnings[1]
                    return False
                return getattr(xizmetker, 'role', None) == "Officiant"

            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', None):
                    self.message = warnings[0]
                    return False
                return request.method in SAFE_METHODS


        if getattr(view, 'action', None) == 'staff':
            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', True):
                    self.message = warnings[0]
                    return False

                return True
            return False
            
        if getattr(view, 'action', None) == 'stock_transactions':
            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', True):
                    self.message = warnings[0]
                    return False

                return True

        if getattr(view, 'action', None) == 'reservations':
            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', True):
                    self.message = warnings[0]
                    return False

                return request.method in SAFE_METHODS

            
            customer = getattr(user, 'customers', None)
            if customer:
                return True
            return False
                    
        return False


    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Offitsiant faqat o'z restoranining kategoriyasini ko'ra oladi
        xizmetker = getattr(user, 'xizmetkerler', None)
        if xizmetker and (getattr(xizmetker, 'role', None) == "Officiant" or 
        getattr(xizmetker, 'role', None)=='Sklad xizmetkeri'):
            return xizmetker.restoran == obj


        # Admin faqat o'z restorani bo'lsa kira oladi
        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restoran', None):
            return admin.restoran == obj

        customer = getattr(user, 'customers', None)
        if customer:
            return request.method in SAFE_METHODS
        
        return False


# categories/id/dishes/
class CategoryDishesPermission(BasePermission):
    """
    Restoran admin ushin  -----  GET, POST(restoran_id)
    Klinet ushin  ----  GET
    Officiant ushin -----  GET (restoran_id)
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if hasattr(user, 'customers') and request.method in SAFE_METHODS:
            return True

        xizmetker = getattr(user, 'xizmetkerler', None)
        if xizmetker:
            if not getattr(xizmetker, 'is_active', True):
                self.message = 'Siz aktiv emessiz!'
                return False
            return getattr(xizmetker, 'role', None) == "Officiant" and request.method in SAFE_METHODS

        admin = getattr(user, 'adminler', None)
        if admin:
            if not getattr(admin, 'is_active', True):
                return False
            return bool(getattr(admin, 'restoran', None))

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(user, 'customers') and request.method in SAFE_METHODS:
            return True

        xizmetker = getattr(user, 'xizmetkerler', None)
        if (xizmetker and getattr(xizmetker, 'role', None) == "Officiant"
        and request.method in SAFE_METHODS):
            return xizmetker.restoran == obj.restoran

        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restoran', None):
            return admin.restoran == obj.restoran
        return False



    
# dishes/id/   AND   dishes/id/toggle-availability/        
class DishTogglePermission(BasePermission):
    """
    Restoran admin ---- GET, PUT, PATCH, DELETE(restoran_id)
    Klient ---- GET
    Officiant --- GET (restoran_id)
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        admin = getattr(user, 'adminler', None)
        if (admin and getattr(admin,'restoran', None)):
            if not getattr(admin, 'is_active', True):
                self.message = "Siz aktiv emessiz!"
                return False
            
            return True

        customer = getattr(user, 'customers',None)
        if (customer and request.method in SAFE_METHODS):
            return True

        waiter = getattr(user, 'xizmetkerler', None)
        if (waiter and getattr(waiter, 'restoran', None) and
        getattr(waiter, 'role', None) == 'Officiant'):
            if not getattr(waiter, 'is_active', True):
                self.message = "Siz Aktiv emessiz!"
                return False
            
            return request.method in SAFE_METHODS

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        admin = getattr(user, 'adminler', None)
        if (admin and getattr(admin, 'restoran', None)):
            return admin.restoran == obj.category.restoran

        waiter = getattr(user, 'xizmetkerler', None)
        if (waiter and getattr(waiter, 'restoran', None) and
        getattr(waiter, 'role', None) == 'Officiant' and request.method in SAFE_METHODS):
            return obj.category.restoran == waiter.restoran

        customer = getattr(user, 'customers', None)
        if (customer and request.method in SAFE_METHODS):
            return True

        return False

        
class IngredientPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        admin = getattr(user, 'adminler', None)
        if (admin and getattr(admin, 'restoran', None)):
            return True


        if getattr(view, 'action', None) == 'stock_in':

            sklad_xizmetker = getattr(user, 'Sklad xizmetkeri', None)
            if (sklad_xizmetker and getattr(sklad_xizmetker, 'restoran', None)):
                return True
            
            admin = getattr(user, 'adminler', None)
            if (admin and getattr(admin, 'restoran', None)):
                return True

            return False

            

        
