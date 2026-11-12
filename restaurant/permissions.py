from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.shortcuts import get_object_or_404
from .models import Category, Dish


warnings = (
     "Siz aktiv emessiz. SuperAdminge xabarlasin",
     "Siz aktiv emessiz. Restoran adminge xabarlasin"
)

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user and user.is_authenticated:
            return False
        customer = getattr(user, 'customers', None)
        if customer:
            return True
        return False




# restaurants/ AND restaurants/id/  
# class SuperANDCustomer(BasePermission):
#     """
#     Superadmin -- GET POST
#     Klient ----- GET
#     """
#     def has_permission(self, request, view):
#         user = request.user
#         if not (user and user.is_authenticated):
#             return False

#         if user.is_superuser:
#             return True

#         if hasattr(user, 'customers') and request.method in SAFE_METHODS:
#             return True

        
#         return False

#     def has_object_permission(self, request, view, obj):
#         user = request.user
#         if user.is_superuser:
#             return True

#         if hasattr(user, 'customers') and request.method in SAFE_METHODS:
#             return True

#         return False


class RestoranAdminUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user and not user.is_authenticated:
            return False

        admin = getattr(user, 'adminler', None)
        if admin:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        admin = getattr(user, 'adminler', None)
        if admin:
            return admin.restaurant == obj

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


        if getattr(view, 'action', None) == 'categories':
            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', True):
                    self.message = warnings[0]
                    return False
                return True

    


                
        # Faqat action `@action(detail=True, ...)` ya'ni `categories` bo'lgandagina 
        # Offitsiant va Adminlar o'tishi mumkin
        if getattr(view, 'action', None) == 'tables':
            xizmetker = getattr(user, 'xizmetkerler', None)
            if xizmetker:
                if not getattr(xizmetker, 'is_active', True):
                    self.message = warnings[1]
                    return False
                
                return (getattr(xizmetker, 'role', None) == "waiter" 
                and request.method in SAFE_METHODS)

            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', True):
                    self.message = warnings[0]
                    return False
                return bool(getattr(admin, 'restaurant', None))
            
            # customer = getattr(user, 'customers', None)
            # if customer:
            #     return request.method in SAFE_METHODS
            return False



        if getattr(view, 'action', None) == 'ingredients':
            xizmetker = getattr(user, 'xizmetkerler', None)
            if xizmetker:
                if not getattr(xizmetker, 'is_active', True):
                    self.message = warnings[1]
                    return False
                if getattr(xizmetker, 'role', None) == 'storekeeper':
                    return True

                return getattr(xizmetker, 'role', None) == 'cook' and request.method in SAFE_METHODS

            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', None):
                    self.message = warnings[0]
                    return False
                return request.method in SAFE_METHODS
            

        if getattr(view, 'action', None) == 'orders':
            xizmetker = getattr(user, 'xizmetkerler', None)
            if xizmetker:
                if not getattr(xizmetker, 'is_active', True):
                    self.message = warnings[1]
                    return False
                return getattr(xizmetker, 'role', None) == "waiter"

            admin = getattr(user, 'adminler', None)
            if admin:
                if not getattr(admin, 'is_active', None):
                    self.message = warnings[0]
                    return False
                return request.method in SAFE_METHODS
            return False


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

            
            xizmetker = getattr(user, 'xizmetkerler', None)
            if xizmetker:
                if not getattr(xizmetker, 'is_active', True):
                    self.message = warnings[1]
                    return False
                return getattr(xizmetker, 'role', None) == 'storekeeper'

            

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

        if getattr(view, 'action', None) == 'stats':
            if user.is_superuser:
                return True
            return False


        if getattr(view, 'action', None) == 'menu':
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
                return True
            if user.is_superuser:
                return True
            return True



        if getattr(view, 'action', None) == 'available_tables':
            customer = getattr(user, 'customers', None)
            if customer:
                return True
            return False
        
        return False

        


    def has_object_permission(self, request, view, obj):
        user = request.user
        
        xizmetker = getattr(user, 'xizmetkerler', None)
        if xizmetker and (getattr(xizmetker, 'role', None) in ['waiter', 'cook', 'storekeeper']):
            return xizmetker.restaurant == obj


        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restaurant', None):
            return admin.restaurant == obj

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
            return getattr(xizmetker, 'role', None) == "waiter" and request.method in SAFE_METHODS

        admin = getattr(user, 'adminler', None)
        if admin:
            if not getattr(admin, 'is_active', True):
                return False
            return bool(getattr(admin, 'restaurant', None))

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(user, 'customers') and request.method in SAFE_METHODS:
            return True

        xizmetker = getattr(user, 'xizmetkerler', None)
        if (xizmetker and getattr(xizmetker, 'role', None) == "waiter"
        and request.method in SAFE_METHODS):
            return xizmetker.restaurant == obj.restaurant

        admin = getattr(user, 'adminler', None)
        if admin and getattr(admin, 'restaurant', None):
            return admin.restaurant == obj.restaurant
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
        xizmetker = getattr(user, 'xizmetkerler', None)

        if (admin and getattr(admin,'restaurant', None)):
            if not getattr(admin, 'is_active', True):
                self.message = "Siz aktiv emessiz!"
                return False
            
            return True

        customer = getattr(user, 'customers',None)
        if (customer and request.method in SAFE_METHODS):
            return True

        waiter = getattr(user, 'xizmetkerler', None)
        if (waiter and getattr(waiter, 'restaurant', None) and
        getattr(waiter, 'role', None) == 'waiter'):
            if not getattr(waiter, 'is_active', True):
                self.message = "Siz Aktiv emessiz!"
                return False
            
            return request.method in SAFE_METHODS



        if getattr(view, 'action', None)  == 'recipe_items':
            if (admin and getattr(admin, 'restaurant', None)):
                if not getattr(admin, 'is_active', True):
                    self.message = "Siz aktiv emessiz!"
                    return False
                return True

            if (xizmetker and getattr(xizmetker, 'restaurant', None) and getattr(xizmetker, 'role', None)=='cook'):
                if not getattr(xizmetker, 'is_active', True):
                    self.message = "Siz aktiv emessiz!"
                    return False
                return request.method in SAFE_METHODS
                            

        if getattr(view, 'action', None) == 'toggle_availability':
            if (admin and getattr(admin, 'restaurant', None)):
                if not getattr(admin, 'is_active', True):
                    self.message = "Siz aktiv emessiz!"
                    return False
                return True

            if(xizmetker and getattr(xizmetker, 'restaurant', None) and getattr(xizmetker, 'role', None)=='cook'):
                if not getattr(xizmetker, 'is_active', True):
                    self.message = "Siz aktiv emessiz!"
                    return False
                return True
        
        return False


    def has_object_permission(self, request, view, obj):
        user = request.user
        admin = getattr(user, 'adminler', None)
        if (admin and getattr(admin, 'restaurant', None)):
            return admin.restaurant == obj.category.restaurant

        waiter = getattr(user, 'xizmetkerler', None)
        if (waiter and getattr(waiter, 'restaurant', None) and
        getattr(waiter, 'role', None) == 'waiter' and request.method in SAFE_METHODS):
            return obj.category.restaurant == waiter.restaurant

        cook = getattr(user, 'xizmetkerler', None)
        if (cook and getattr(cook, 'role', None)=='cook'):
            if getattr(view, 'action', None)=='toggle_availability':
                return obj.category.restaurant == cook.restaurant
            return request.method in SAFE_METHODS

        
        customer = getattr(user, 'customers', None)
        if (customer and request.method in SAFE_METHODS):
            return True

        return False

    
# receptItem/id/ 
class ReceptItemPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False

        admin = getattr(request.user, 'adminler', None)
        if admin:
            if not getattr(admin, 'is_active', True):
                self.message = warnings[0]
                return False
            return True

        return False

    def has_object_permission(self, request, view, obj):
        admin = getattr(request.user, 'adminler', None)
        if hasattr(obj, 'dish'):
            return admin.restaurant == obj.dish.category.restaurant

        return False



class IngredientPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        admin = getattr(user, 'adminler', None)
        if (admin and getattr(admin, 'restaurant', None)):
            if not getattr(admin, 'is_active', None):
                self.message = warnings[0]
                return False            
            return True

        sklad_xizmetker = getattr(user, 'xizmetkerler', None)
        if (sklad_xizmetker and getattr(sklad_xizmetker, 'restaurant', None)):
            if not getattr(sklad_xizmetker, 'is_active', None):
                self.message = warnings[1]
                return False
            return True

        if getattr(view, 'action', None) == 'stock_in':

            if (sklad_xizmetker and getattr(sklad_xizmetker, 'restaurant', None)
            and getattr(sklad_xizmetker, 'role', None)=='storekeeper'):
                return True
            
            admin = getattr(user, 'adminler', None)
            if (admin and getattr(admin, 'restaurant', None)):
                return True
        
            return False

        if getattr(view, 'action', None) == 'stock_out':
            if (sklad_xizmetker and getattr(sklad_xizmetker, 'restaurant', None) 
            and getattr(sklad_xizmetker, 'role', None)=='storekeeper'):
                return True

            return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        admin = getattr(user, 'adminler', None)
        sklad = getattr(user, 'xizmetkerler', None)

        if admin and getattr(admin, 'restaurant',  None):
            if not getattr(user, 'is_active', True):
                self.message = warnings[0]
                return False

            return obj.restaurant == admin.restaurant


        if (sklad and getattr(sklad, 'restaurant', None) 
        and getattr(sklad, 'role', None)=='storekeeper'):
            if not getattr(sklad, 'is_active', None):
                self.message = warnings[1]
                return False

            return obj.restaurant == sklad.restaurant
        
        return False