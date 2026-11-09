from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework import mixins, status
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from USErs.serializer import (
    XizmetkerSerializer
)


from .serializers import (
    RestaurantListSerializer, 
    CategoryListSerializer, DishListSerializer, 
    DishCreateSerializer,DishStoplistSerializer, 
    TableListSerializer,ReceptItemSerializer, 
    IngredientSerializer, IngredientDetailSerializer,DishStopResponseSerializer,
    DishDetailSerializer,IngredientAddSerializer, 
    StockTransationSerializer, RestaurantCustomerListSerializer,
    CategoryEditSerializer, MenuSerializer, IngredientSubtractSerializer
)

from order.serializers import OrderListSerializer
from reservation.serializers import (
    ReservationCreateSerializer, 
    ReservationListSerializer
)


from . import models

from .permissions import (
    CategoryIngredientTableOrderListPermission, 
    CategoryDishesPermission, DishTogglePermission, 
    IngredientPermission, ReceptItemPermission, 
    RestoranAdminUpdatePermission, IsCustomer
)
from reservation.permissions import ReservationPermission
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser


# api/restaurants/, api/restaurants/id , actions = ['categories', 'staff', 'reservations', 'tables', 'ingredients', 'stock-transactions', 'menu', 'stats']
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = models.Restaurant.objects.all()
    serializer_class = RestaurantListSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'address']

    filterset_fields = ['is_active']


    def filter_queryset(self, queryset):
        if self.action != 'list':
            return queryset
        return super().filter_queryset(queryset)



    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        if self.action in ['update', 'partial_update', 'destroy']:
            if self.action in ['update', 'partial_update']:
                return [RestoranAdminUpdatePermission()]
            return [IsAdminUser()]
        
        if self.action == 'reservations':
            return [ReservationPermission()]

        if self.action == 'stats':
            return [AllowAny()]

        if self.action == 'available_tables':
            return [IsCustomer()]
        
        return [CategoryIngredientTableOrderListPermission()]

    

    def get_serializer_class(self):
        if self.action == 'ingredients':
            return IngredientSerializer

        if self.action == 'menu':
            return MenuSerializer
        
        
        if self.action == 'categories':
            return CategoryListSerializer

        
        if self.action == 'reservations':
            if self.request.method == "POST":
                return ReservationCreateSerializer
            return ReservationListSerializer

        if self.action == 'stock_transactions':
            return StockTransationSerializer

        

        if self.action =='available_tables':
            return TableListSerializer
            
        if not self.request.user.is_superuser or self.action == 'retrieve':
            return RestaurantCustomerListSerializer
        
        return super().get_serializer_class()



    #restaurants/id/menu/
    @extend_schema(methods=['GET'], responses={200: MenuSerializer(many=True)})
    @action(detail=True, methods=['get'], url_path='menu')
    def menu(self, request, pk=None):
        restaurant = self.get_object()
        menu = restaurant.categories.all()
        serializer = self.get_serializer(menu, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    







    # restaurants/id/categories/
    @extend_schema(methods=['POST'], request=CategoryListSerializer, responses={201:CategoryListSerializer}, filters=False)
    @action(detail=True, methods=['post'], url_path='categories')
    def categories(self, request, pk=None):
        restaurant = self.get_object()


        if request.method == 'POST':
            serializer = CategoryListSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)




    # restaurants/id/tables/
    @extend_schema(methods=['get'], responses={200:TableListSerializer(many=True)}, filters=False)
    @extend_schema(methods=['post'], request=TableListSerializer, responses={201:TableListSerializer}, filters=False)
    @action(detail=True, methods=['get', 'post'], url_path='tables')
    def tables(self, request, pk=None):
        restaurant = self.get_object()
        if request.method == "GET":
            tables = restaurant.tables.all()

            serializer = TableListSerializer(tables, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "POST":
            serializer = TableListSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/ingredients/
    @extend_schema(methods=['get'], responses={200:IngredientSerializer(many=True)}, filters=False)
    @extend_schema(methods=['post'], request=IngredientSerializer, responses={201:IngredientSerializer}, filters=False)
    @action(detail=True, methods=['get', 'post'], url_path='ingredients')
    def ingredients(self, request, pk=None):
        restaurant = self.get_object()
        if request.method == "GET":
            ingredients = restaurant.ingredients.all()
            serializer = IngredientSerializer(ingredients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            serializer = IngredientSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/staff/
    @extend_schema(methods=['GET'], responses={200:XizmetkerSerializer(many=True)}, filters=False)
    @extend_schema(methods=['POST'], request=XizmetkerSerializer, responses={201:XizmetkerSerializer}, filters=False)
    @action(detail=True, methods=['get', 'post'], url_path='staff')
    def staff(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == 'GET':
            staff = restaurant.staff.all()
            serializer = XizmetkerSerializer(staff, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "POST":
            serializer = XizmetkerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # # # restaurants/id/reservations/
    # @extend_schema(methods=['GET'], responses={200: ReservationListSerializer(many=True)}, filters=False)
    # @extend_schema(methods=['POST'], request=ReservationCreateSerializer, responses={201: ReservationListSerializer}, filters=False)
    # @action(detail=True, methods=['get', 'post'], url_path='reservations')
    # def reservations(self, request, pk=None):
    #     restaurant = self.get_object()

    #     if request.method == "GET":
    #         reservations = restaurant.reservations.filter(status__in = ['pending', 'confirmed']).select_related('client__user', 'restaurant', 'table').all()
    #         serializer = self.get_serializer(reservations, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     if request.method == "POST":
    #         serializer = self.get_serializer(data=request.data)
    #         if serializer.is_valid():
    #             customer = getattr(request.user, 'customers', None)
    #             serializer.save(restaurant=restaurant, client=customer)
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/orders/
    @extend_schema(methods=['GET'],responses={200: OrderListSerializer(many=True)},filters=False)
    @extend_schema(methods=['POST'],request=OrderListSerializer, responses={201: OrderListSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='orders')
    def orders(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == 'GET':
            xizmetker = getattr(request.user, 'xizmetkerler', None)
            if xizmetker:
                orders = restaurant.orders.filter(waiter = xizmetker).order_by('-closed_at')
                serializer = OrderListSerializer(orders, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)


            orders = restaurant.orders.all()
            serializer = OrderListSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)



        if request.method == 'POST':
            serializer = OrderListSerializer(data=request.data)
            if serializer.is_valid():

                xizmetker = getattr(request.user, 'xizmetkerler', None)

                serializer.save(restaurant=restaurant, waiter=xizmetker)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/stock-transactions/
    @extend_schema(methods=['GET'], responses={200:StockTransationSerializer(many=True)}, filters=False)
    @action(detail=True, methods=['get'], url_path='stock-transactions')
    def stock_transactions(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == 'GET':
            transactions = models.StockTransaction.objects.filter(ingredient__in=restaurant.ingredients.all()).order_by('-created_at')
            serializer = StockTransationSerializer(transactions, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)



    # api/restaurants/id/available-tables/
    @extend_schema(methods=['GET'], responses={200: TableListSerializer(many=True)}, filters=False)
    @action(detail=True, methods=['get'], url_path='available-tables')
    def available_tables(self, request, pk=None):
        restaurant = self.get_object()

        tables = restaurant.tables.filter(restaurant=restaurant, status='free')
        serializer = self.get_serializer(tables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    # # api/restaurants/stats/
    @extend_schema(methods=['GET'], responses={200: dict})
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        all_restaurant = models.Restaurant.objects.all().count()
        is_active_restaurant = models.Restaurant.objects.filter(is_active=True).count()
        not_active_restaurant = models.Restaurant.objects.filter(is_active=False).count()
        admin_null = models.Restaurant.objects.filter(admin__isnull=True).count()
        
        return Response(
            {
                "total": all_restaurant,
                "active": is_active_restaurant,
                'inactive': not_active_restaurant,
                'without_admin': admin_null
            },

            status=status.HTTP_200_OK
        )
        


#categories/id/
class CategoryViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):

    queryset = models.Category.objects.all()
    serializer_class = CategoryListSerializer
    permission_classes = [CategoryDishesPermission]
    http_method_names = ['patch', 'delete', 'post', 'get']

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return CategoryEditSerializer
        if self.action == 'dishes':
            if self.request.method == "POST":
                return DishCreateSerializer
            return DishListSerializer
        
        return super().get_serializer_class()   



    # categories/id/dishes/
    @extend_schema(methods=['GET'], responses={200: DishListSerializer(many=True)})
    @extend_schema(methods=['POST'], request=DishCreateSerializer, responses={201: DishListSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='dishes')
    def dishes(self, request, pk=None):
        category = self.get_object()

        if request.method == "GET":
            dishes = category.dishes.all()
            user = self.request.user

            is_admin = (
            user.is_authenticated and 
            hasattr(user, 'adminler') and 
            getattr(user.adminler, 'is_active', True) and
            getattr(user.adminler, 'restaurant', None) is not None
        )

            if not is_admin:
                dishes = dishes.filter(is_available=True)


            serializer = self.get_serializer(dishes, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(category=category)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# dishes/id/             
class DishDetailReceptItemView(mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet
                               ):
    
    queryset = models.Dish.objects.all()
    serializer_class = DishDetailSerializer
    permission_classes = [DishTogglePermission]
    pagination_class = None
    http_method_names = ['patch', 'delete', 'post', 'get']



    # dishes/id/recipe-items/
    @extend_schema(methods=['get'], responses={200: ReceptItemSerializer(many=True)})
    @extend_schema(methods=['post'], request=ReceptItemSerializer, responses={201:ReceptItemSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='recipe-items', serializer_class=ReceptItemSerializer)
    def recipe_items(self, request, pk=None):
        dish = self.get_object()

        if request.method == 'GET':
            recept_items = dish.recept_items.all()
            serializer = ReceptItemSerializer(recept_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "POST":
            serializer = ReceptItemSerializer(data = request.data)
            if serializer.is_valid():
                ingredient_id = serializer.validated_data.get('ingredient')
                if models.ReceptItem.objects.filter(dish=dish, ingredient=ingredient_id).exists():
                    return Response(
                        {'detail': "Bul ingredient usi tagamga alleqashan qosilgan!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer.save(dish=dish)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    # dishes/id/toggle-availability/
    @extend_schema(methods=['patch'], request=DishStoplistSerializer, responses=DishStopResponseSerializer)
    @action(detail=True, methods=['patch'], url_path='toggle-availability')
    def toggle_availability(self, request, pk=None):
        dish = self.get_object()

        serializer = DishStoplistSerializer(dish, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceptItemDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.ReceptItem.objects.all()
    serializer_class = ReceptItemSerializer
    http_method_names = ['patch', 'delete']
    permission_classes = [ReceptItemPermission]


# ingredient/id/
class IngredientDetailStockView(mixins.RetrieveModelMixin, 
                                viewsets.GenericViewSet):

    queryset = models.Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get', 'patch']
    permission_classes = [IngredientPermission]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'stock_in':
            return IngredientAddSerializer
        if self.action == 'stock_out':
            return IngredientSubtractSerializer
        return super().get_serializer_class()




    # ingredient/id/stock-in/
    @extend_schema(methods=['PATCH'], request=IngredientAddSerializer, responses=IngredientDetailSerializer)
    @action(detail=True, methods=['patch'], url_path='stock-in')
    def stock_in(self, request, pk=None):
        ingredient = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']
        ingredient = self.get_object()

        ingredient.current_stock += quantity
        ingredient.save()

        models.StockTransaction.objects.create(
            type='in', ingredient = ingredient, reason=f"Skladqa {quantity} {ingredient.unit} {ingredient.name} qosildi!",
            quantity = quantity
        )

        return Response({"detail": "Ingredient Skladqa tabisli qosildi!"}, status=status.HTTP_200_OK)


    # ingredients/id/stock-out/
    @extend_schema(methods=['PATCH'], request=IngredientSubtractSerializer, responses={200:IngredientSerializer})
    @action(detail=True, methods=['patch'], url_path='stock-out')
    def stock_out(self, request, pk=None):
        ingredient = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']
        reason = serializer.validated_data['reason']

        ingredient.current_stock -= quantity
        ingredient.save()

        models.StockTransaction.objects.create(
            type='out', ingredient=ingredient, reason=f"{reason} --- {ingredient.name} -- {quantity} mugdar alinip taslandi!", quantity=quantity
        )

        response_data = IngredientSerializer(ingredient)
        return Response(response_data.data, status=status.HTTP_200_OK)





class TableViewSet(mixins.RetrieveModelMixin, 
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):

    queryset = models.Table.objects.all()
    serializer_class = TableListSerializer
    permission_classes = [CategoryDishesPermission]
    pagination_class=None






