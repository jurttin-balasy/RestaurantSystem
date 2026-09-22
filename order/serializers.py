from rest_framework.serializers import (
    ModelSerializer, IntegerField, CharField,
    SerializerMethodField, ChoiceField, 
    Serializer, DecimalField, ReadOnlyField, ValidationError
)

from . import models
from django.utils import timezone

from drf_spectacular.utils import extend_schema_field





class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ('id', 'order', 'dish', 'quantity', 'status', 'note')
        read_only_fields = ('order', 'status')



class OrderItemUpdateSerializer(ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ('id', 'order', 'dish', 'quantity', 'status', 'note')
        read_only_fields = ('order', 'status')


class OrderItemQuantitySerializer(ModelSerializer):
    quantity_add = IntegerField(write_only=True, required=True, min_value=1)

    class Meta:
        model = models.OrderItem
        fields = ('id', 'order', 'dish', 'quantity_add')
        read_only_fields = ('id', 'order', 'dish', 'quantity')


class OrderItemListSerializer(ModelSerializer):
    dish = CharField(source = 'dish.name', read_only=True)
    dish_price = DecimalField(source='dish.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = ReadOnlyField()
        
    
    class Meta:
        model = models.OrderItem
        fields = ('id', 'order', 'dish', 'dish_price', 'quantity', 'status', 'note', 'total_price')
        read_only_fields = ('order', 'status')

class KitchenOrderItemSerializer(ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ('id', 'order', 'dish', 'quantity', 'status', 'note')
        read_only_fields = ('order','dish', 'note', 'quantity')


class KDSOrderItemSerializer(ModelSerializer):
    table_number = CharField(
        source="order.table.number", read_only=True
    )
    dish_name = CharField(source="dish.name", read_only=True)
    waiter_name = SerializerMethodField()
    waiting_time_minutes = SerializerMethodField()

    class Meta:
        model = models.OrderItem
        fields = [
            "id",
            "order",
            "table_number",
            "dish_name",
            "quantity",
            "status",
            "waiter_name",
            "waiting_time_minutes",
        ]
    @extend_schema_field(IntegerField())
    def get_waiter_name(self, obj):
        if obj.order.waiter:
            return (
                f"{obj.order.waiter.user.first_name} {obj.order.waiter.user.last_name}"
            )
        return "Noma'lum"

    @extend_schema_field(IntegerField())
    def get_waiting_time_minutes(self, obj):
        if obj.order.created_at:
            now = timezone.now()
            diff = now - obj.order.created_at
            return int(diff.total_seconds() // 60)
        return 0


class OrderListSerializer(ModelSerializer):
    order_items = OrderItemListSerializer(many=True, read_only=True)
    total_order_price = ReadOnlyField()
    table_number = IntegerField(source='table.number', read_only=True)

    def create(self, validated_data):
        order = super().create(validated_data)
        if order.table:
            if order.table.status == 'bant':
                raise ValidationError({'detail': 'Bul stol bant!'})
            
            order.table.status = 'bant'
            order.table.save(update_fields=['status'])
        return order

    
    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)

        if new_status == 'CL' and instance.table:
            table = instance.table
            table.status = 'bos'
            table.save()

        instance.status = new_status
        instance.save()
        return instance


    
    class Meta:
        model = models.Order
        fields = ('id', 'restoran', 'waiter','table', 'table_number', 'status', 'paymend_method', 'order_items', 'total_order_price')
        read_only_fields = ('restoran', 'waiter')


class KDSStatusUpdateSerializer(Serializer):
    status = ChoiceField(
        choices=["TA", "T"],
        required=True,
        error_messages={
            "invalid_choice": "Oshpaz faqat 'TA' (Tayyorlanmoqda) yoki 'T' (Tayyor) statusiga o'tkaza oladi!"
        },
    )


class OrderChangeStatusSerializer(ModelSerializer):
    class Meta:
        model = models.Order
        fields = ('status',)