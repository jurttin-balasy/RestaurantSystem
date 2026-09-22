from rest_framework import generics, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from . import models
from restaurant.models import StockTransaction, Ingredient



from django.db import transaction
from django.db.models import F 
from collections import defaultdict
from decimal import Decimal


from .serializers import (
    OrderListSerializer, OrderItemListSerializer,
    OrderItemSerializer,
    OrderItemQuantitySerializer, OrderItemUpdateSerializer,
    KDSOrderItemSerializer, KDSStatusUpdateSerializer, 
    OrderChangeStatusSerializer, OrderDetailSerializer
)


from .permissions import (
    OrderItemPermission,OrderItemUpdatePermision,
    IsKitchenStaffPermission
)

# orders/id/order_items/
class OrderItemView(mixins.RetrieveModelMixin, 
                    mixins.UpdateModelMixin,mixins.DestroyModelMixin, 
                    viewsets.GenericViewSet):
    
    queryset = models.Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [OrderItemPermission]
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']



    def get_serializer_class(self):
        if self.action == 'order_items':
            if self.request.method == "POST":
                return OrderItemSerializer
            return OrderItemListSerializer
        if self.action == 'change_status' and self.request.method == "PATCH":
            return OrderChangeStatusSerializer

        if self.action in ['update', 'partial_update']:
            return OrderDetailSerializer
        
        return OrderListSerializer


    @extend_schema(methods=["PATCH"], request=OrderChangeStatusSerializer, responses={200:OrderChangeStatusSerializer})
    @action(detail=True, methods=['patch'], url_path='change_status')
    def change_status(self, request, pk=None):
        order = self.get_object()

        if order.status == 'CL':
            raise ValidationError({'detail': "Siz bul orderdi qayta asha almaysiz"})


        serializer = self.get_serializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            order.table.status = 'bos'
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


    @extend_schema(methods=['GET'], responses={200:OrderItemListSerializer(many=True)})
    @extend_schema(methods=['POST'], request=OrderItemSerializer, responses={201: OrderItemSerializer})
    @action(detail=True, methods=['get', 'post'], url_path='order_items')
    def order_items(self, request, pk=None):
        order = self.get_object()

        if request.method == "GET":
            order_items = order.order_items.all()
            serializer = self.get_serializer(order_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                dish = serializer.validated_data.get('dish')
                if not dish.is_available:
                    raise ValidationError(
                        {"message": "Bul tagam tawsilgan!"}
                    )
                
                serializer.save(order=order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(request=None, responses={200: dict})
    @action(detail=True, methods=['post'], url_path='send_to_kitchen')
    def send_to_kitchen(self, request, pk=None):
        order = self.get_object()

        # N+1 so'rov oldini olish uchun recept_items va ingredient-ni birgalikda yuklaymiz
        pending_items = order.order_items.filter(status="J").select_related('dish').prefetch_related('dish__recept_items__ingredient')

        if not pending_items.exists():
            raise ValidationError({"detail": "Bul buyirtpada aspazxanaga jiberiletin tagamalar tabilmadi!"})

        with transaction.atomic():
            required_totals = defaultdict(Decimal)

            # 1-BOSQICH: Barcha taomlar uchun kerakli masaliqlar miqdorini hisoblab chiqamiz
            for item in pending_items:
                dish = item.dish
                for recept_item in dish.recept_items.all():
                    ingredient = recept_item.ingredient
                    if not ingredient:
                        continue

                    unit = recept_item.unit

                    if unit in ['gr', 'ml']:
                        required_quantity = (Decimal(str(recept_item.quantity_per_serving)) / Decimal('1000')) * item.quantity
                    elif unit == 'mg':
                        required_quantity = (Decimal(str(recept_item.quantity_per_serving)) / Decimal('1000000')) * item.quantity
                    else:
                        required_quantity = Decimal(str(recept_item.quantity_per_serving)) * item.quantity

                    required_totals[ingredient.id] += required_quantity

            if required_totals:
                ingredient_ids = list(required_totals.keys())

                # 2-BOSQICH: Ingredientlarni xavfsiz holatda qulflaymiz (select_for_update)
                locked_ingredients = Ingredient.objects.filter(id__in=ingredient_ids).select_for_update()
                ingredient_map = {ing.id: ing for ing in locked_ingredients}

                # 3-BOSQICH: Ombordagi zaxirani tekshiramiz
                for ing_id, total_required in required_totals.items():
                    db_ingredient = ingredient_map.get(ing_id)

                    if not db_ingredient or db_ingredient.current_stock < total_required:
                        raise ValidationError(
                            {"detail": "Skladta ingredientler jetkiliksiz!"}
                        )

                # 4-BOSQICH: Ombordan ayiramiz va tranzaksiya tarixini yaratamiz
                stock_transactions = []
                for ing_id, total_required in required_totals.items():
                    Ingredient.objects.filter(id=ing_id).update(current_stock=F('current_stock') - total_required)

                    stock_transactions.append(
                        StockTransaction(
                            type="out",
                            ingredient_id=ing_id,
                            quantity=total_required,
                            reason=f"#{order.id} ushin {total_required} mugdar ingredient sheship alindi!"
                        )
                    )

                # Tranzaksiyalarni bitta so'rovda saqlaymiz
                StockTransaction.objects.bulk_create(stock_transactions)

            # 5-BOSQICH: Taomlar holatini yangilaymiz
            pending_items.update(status='AJ')

        return Response({"detail": "Tagamlar aspazxanaga jiberildi!"}, status=status.HTTP_200_OK)

        












# order_items/id/  --- GET, PUT
# order_items/id/quantity/  --- PATCH(quantity)
class OrderItemDetailView(
                mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                viewsets.GenericViewSet):

    queryset = models.OrderItem.objects.all()
    serializer_class = OrderItemUpdateSerializer
    permission_classes = [IsAuthenticated, OrderItemUpdatePermision]
    http_method_names = ['get', 'put', 'delete', 'patch']
    
    def get_serializer_class(self):
        if self.action == 'quantity':
            if self.request.method == 'PATCH':
                return OrderItemQuantitySerializer
        return OrderItemUpdateSerializer
    
    def get_queryset(self):
        user = self.request.user
        xizmetker = getattr(user, "xizmetkerler", None)
        if xizmetker:
            return models.OrderItem.objects.filter(
                order__restoran=xizmetker.restoran
            )
        return models.OrderItem.objects.none()

    @action(detail=True, methods=["patch"], url_path="quantity")
    def quantity(self, request, pk=None):
        order_item = self.get_object()  # Permission shu yerda 'J' statusini tekshiradi

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        add_quantity = serializer.validated_data["quantity_add"]

      
        with transaction.atomic():
            order_item.quantity = F("quantity") + add_quantity
            order_item.save(update_fields=["quantity"])

        order_item.refresh_from_db()

        # Janalangan obyektti serializatsiya qilip qaytaramiz
        return Response(
            OrderItemSerializer(order_item).data, status=status.HTTP_200_OK
        )


    




# kitchen/order_items/
class KDSOrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Oshpazxona ekrani (KDS) uchun ViewSet.

    Faqat 'AJ' va 'TA' statusdagi taomlar ko'rinadi.
    """

    queryset = models.OrderItem.objects.all()
    serializer_class = KDSOrderItemSerializer
    permission_classes = [IsAuthenticated, IsKitchenStaffPermission]

    def get_queryset(self):
        user = self.request.user
        xizmetker = getattr(user, "xizmetkerler", None)

        if not xizmetker:
            return models.OrderItem.objects.none()

        # 1. Faqat oshpaz ishlayotgan restoranga tegishli taomlar
        # 2. Statusi faqat 'AJ' (Oshpazxonaga kelgan) va 'TA' (Tayyorlanayotgan)
        # 3. Order yaratilgan vaqti (order__created_at) bo'yicha saralash
        return (
            models.OrderItem.objects.filter(
                order__restoran=xizmetker.restoran, status__in=["AJ", "TA"]
            )
            .select_related("dish", "order", "order__table", "order__waiter")
            .order_by("order__created_at")
        )


    @extend_schema(
        request= KDSStatusUpdateSerializer,
        responses={200:KDSOrderItemSerializer},
    )
    @action(detail=True, methods=["patch"], url_path="change-status")
    def change_status(self, request, pk=None):
        order_item = self.get_object()

        serializer = KDSStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]

        ALLOWED_KITCHEN_STATUSES = ["TA", "T"]

        if new_status not in ALLOWED_KITCHEN_STATUSES:
            raise ValidationError(
                {
                    "status": f"Aspaz statusni faqat {ALLOWED_KITCHEN_STATUSES} ga o'zgartira oladi!"
                }
            )

        
        order_item.status = new_status
        order_item.save(update_fields=["status"])

        # Status 'T' (Tayyor) bo'lsa, bu item avtomat get_queryset ro'yxatidan yo'qoladi
        return Response(
            KDSOrderItemSerializer(order_item).data,
            status=status.HTTP_200_OK,
        )


















# class SendToKitchenView(APIView):
#     def post(self, request, order_id):
#         order = get_object_or_404(models.Order, id=order_id)
        
#         user = request.user
#         xizmetker = getattr(user, 'xizmetkerler', None)
        
#         if not xizmetker or xizmetker.restoran != order.restoran or xizmetker.role != "Officiant":
#             return Response({"error": "Sizda bu buyurtmani oshpazxonaga yuborish huquqi yo'q!"}, status=status.HTTP_403_FORBIDDEN)

#         new_items = order.order_items.filter(status='J')
#         if not new_items.exists():
#             return Response({"error": "Yuborish uchun yangi taomlar topilmadi."}, status=status.HTTP_400_BAD_REQUEST)

#         missing_ingredients = []

#         with transaction.atomic():
#             for item in new_items:
#                 dish = item.dish
#                 multiplier = item.quantity
#                 recipe_items = dish.recept_items.all()

#                 for recipe in recipe_items:
#                     ingredient = recipe.ingredient
#                     required_qty = recipe.quantity_per_serving * multiplier
                    
#                     if ingredient.current_stock < required_qty:
#                         missing_ingredients.append({
#                             "dish": dish.name,
#                             "ingredient": ingredient.name,
#                             "required": float(required_qty),
#                             "available": float(ingredient.current_stock),
#                             "unit": ingredient.unit
#                         })

#             if missing_ingredients:
#                 return Response({
#                     "error": "Omborda yetarli masalliq yo'q!",
#                     "missing_items": missing_ingredients
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             for item in new_items:
#                 dish = item.dish
#                 multiplier = item.quantity
#                 recipe_items = dish.recept_items.all()

#                 for recipe in recipe_items:
#                     unit = recipe.unit
#                     ingredient = recipe.ingredient
#                     required_qty = recipe.quantity_per_serving * multiplier

#                     if unit =='gr':
#                         ingredient.current_stock -= required_qty / 1000
#                         ingredient.save()
#                     if unit == 'mg':
#                         ingredient.current_stock -= required_qty / 1000000
#                         ingredient.save()
#                     if unit == 'ml':
#                         ingredient.current_stock -= required_qty / 1000
#                         ingredient.save() 

#                     ingredient.current_stock -= required_qty
#                     ingredient.save()

                    
#                     StockTransaction.objects.create(
#                         type='out',
#                         quantity=required_qty,
#                         reason=f"Order #{order.id} - {dish.name}",
#                         ingredient=ingredient
#                     )

#                 item.status = 'AJ'
#                 item.save()

#         return Response({"message": "Buyurtpalar aspazxanaga jiberildi ham ingredientler sheshildi!"}, status=status.HTTP_200_OK)