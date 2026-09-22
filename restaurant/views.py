from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import mixins, status

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from rest_framework import permissions

from USErs.serializer import (
    XizmetkerSerializer
)

from .serializers import (
    RestaurantListSerializer, 
    CategoryListSerializer, 
    DishListSerializer, DishCreateSerializer,
    DishStoplistSerializer, 
    TableListSerializer, TableBookSerializer, 
    ReceptItemSerializer, IngredientSerializer,
    IngredientDetailSerializer,DishDetailSerializer,
    IngredientAddSerializer, StockTransationSerializer,

)

from order.serializers import OrderListSerializer
from reservation.serializers import (
    ReservationCreateSerializer, 
    ReservationListSerializer
)


from . import models

from .permissions import (
    SuperANDCustomer, CategoryIngredientTableOrderListPermission, 
    CategoryDishesPermission, DishTogglePermission
)
from USErs.permissions import IsRestoranAdmin
from reservation.permissions import ReservationPermission

# api/restaurants, api/restaurants/id -- list
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = models.Restaurant.objects.all()
    serializer_class = RestaurantListSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy', 'create']:
            return [SuperANDCustomer()]

        if self.action == 'reservations':
            return [ReservationPermission()]
        
        return [CategoryIngredientTableOrderListPermission()]

    def get_serializer_class(self):
        if self.action == 'ingredients':
            return IngredientSerializer
        if self.action == 'categories':
            return CategoryListSerializer
        if self.action == 'reservations':
            if self.request.method == "POST":
                return ReservationCreateSerializer
            return ReservationListSerializer
            
        return super().get_serializer_class()



    # restaurants/id/categories/
    @extend_schema(methods=['get'], responses={200:CategoryListSerializer(many=True)})
    @extend_schema(methods=['post'], request=CategoryListSerializer, responses={201:CategoryListSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='categories')
    def categories(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == "GET":
            categories = restaurant.categories.all()
            serializer = CategoryListSerializer(categories, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            serializer = CategoryListSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(restoran=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)



    # restaurants/id/tables/
    @extend_schema(methods=['get'], responses={200:TableListSerializer(many=True)})
    @extend_schema(methods=['post'], request=TableListSerializer, responses={201:TableListSerializer})
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
                serializer.save(restoran=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/ingredients/
    @extend_schema(methods=['get'], responses={200:IngredientSerializer(many=True)})
    @extend_schema(methods=['post'], request=IngredientSerializer, responses={201:IngredientSerializer})
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
                serializer.save(restoran=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/staff/
    @extend_schema(methods=['GET'], responses={200:XizmetkerSerializer})
    @extend_schema(methods=['POST'], request=XizmetkerSerializer, responses={201:XizmetkerSerializer})
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
                serializer.save(restoran=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # # restaurants/id/reservations/
    @extend_schema(methods=['GET'], responses={200: ReservationListSerializer(many=True)})
    @extend_schema(methods=['POST'], request=ReservationCreateSerializer, responses={201: ReservationListSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='reservations')
    def reservations(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == "GET":
            reservations = restaurant.reservations.filter(status__in = ['jaratildi', 'tastiyiqlandi']).select_related('client__user', 'restoran', 'table').all()
            serializer = self.get_serializer(reservations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                customer = getattr(request.user, 'customers', None)
                serializer.save(restoran=restaurant, client=customer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/orders/
    @extend_schema(methods=['GET'],responses={200: OrderListSerializer(many=True)})
    @extend_schema(methods=['POST'],request=OrderListSerializer, responses={201: OrderListSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='orders')
    def orders(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == 'GET':
            xizmetker = getattr(request.user, 'xizmetkerler', None)
            if xizmetker:
                orders = restaurant.orders.filter(waiter = xizmetker, status='Q')
                serializer = OrderListSerializer(orders, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)


            orders = restaurant.orders.all()
            serializer = OrderListSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)



        if request.method == 'POST':
            serializer = OrderListSerializer(data=request.data)
            if serializer.is_valid():
                xizmetker = getattr(request.user, 'xizmetkerler', None)

                serializer.save(restoran=restaurant, waiter=xizmetker)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # restaurants/id/stock_transactions/
    @extend_schema(methods=['GET'], responses={200:StockTransationSerializer(many=True)})
    @action(detail=True, methods=['get'], url_path='stock_transactions')
    def stock_transactions(self, request, pk=None):
        restaurant = self.get_object()

        if request.method == 'GET':
            transactions = models.StockTransaction.objects.filter(ingredient__in=restaurant.ingredients.all())
            serializer = StockTransationSerializer(transactions, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)


    








#categories/id/
class CategoryViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):

    queryset = models.Category.objects.all()
    serializer_class = CategoryListSerializer
    permission_classes = [CategoryDishesPermission]

    def get_serializer_class(self):
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
            getattr(user.adminler, 'restoran', None) is not None
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


    # dishes/id/recept-items/
    @extend_schema(methods=['get'], responses={200: ReceptItemSerializer(many=True)})
    @extend_schema(methods=['post'], request=ReceptItemSerializer, responses={201:ReceptItemSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='recept-items', serializer_class=ReceptItemSerializer)
    def recep_items(self, request, pk=None):
        dish = self.get_object()

        if request.method == 'GET':
            recept_items = dish.recept_items.all()
            serializer = ReceptItemSerializer(recept_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "POST":
            serializer = ReceptItemSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(dish=dish)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    # dishes/id/toggle-availability
    @extend_schema(methods=['patch'], request=DishStoplistSerializer, responses=DishDetailSerializer)
    @action(detail=True, methods=['patch'], url_path='toggle-availability')
    def toggle_availability(self, request, pk=None):
        dish = self.get_object()

        serializer = DishStoplistSerializer(dish, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# ingredient/id/
class IngredientDetailStockView(mixins.RetrieveModelMixin, 
                                viewsets.GenericViewSet):

    queryset = models.Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get', 'patch']

    def get_serializer_class(self):
        if self.action == 'stock_in':
            return IngredientAddSerializer
        return super().get_serializer_class()




    # ingredient/id/stock-in/
    @extend_schema(methods=['PATCH'], request=IngredientAddSerializer, responses=IngredientDetailSerializer)
    @action(detail=True, methods=['patch'], url_path='stock_in')
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






class TableViewSet(mixins.RetrieveModelMixin, 
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):

    queryset = models.Table.objects.all()
    serializer_class = TableListSerializer
    permission_classes = [CategoryDishesPermission]

