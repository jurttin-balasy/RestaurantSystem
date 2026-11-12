from . import models
from rest_framework.serializers import (
    ModelSerializer, DecimalField, 
    ValidationError, TimeField, ReadOnlyField,
    CharField, SerializerMethodField
)

from USErs.models import RestoranAdminmodel

class AdminMiniSerializer(ModelSerializer):
    phone_number = ReadOnlyField(source='user.phone_number')
    first_name = ReadOnlyField(source='user.first_name')
    last_name = ReadOnlyField(source='user.last_name')

    class Meta:
        model = RestoranAdminmodel
        fields = ('id', 'phone_number', 'first_name', 'last_name')


class RestaurantListSerializer(ModelSerializer):
    start_time = TimeField(
            format='%H:%M',
            input_formats=['%H:%M', '%H-%M']
        )

    end_time = TimeField(
        format='%H:%M',
        input_formats=['%H:%M', '%H-%M']
    )


    admin = SerializerMethodField(read_only=True)

    class Meta:
        model = models.Restaurant
        fields = ('id', 'name', 'address', 'phone', 'is_active', 'start_time', 'end_time', 'admin')

    def get_admin(self, obj):
        admin = RestoranAdminmodel.objects.filter(restaurant=obj).first()
        if not admin:
            return None

        serializer = AdminMiniSerializer(admin)
        return serializer.data






class RestaurantCustomerListSerializer(ModelSerializer):
    start_time = TimeField(
            format='%H:%M',
            input_formats=['%H:%M', '%H-%M']
        )

    end_time = TimeField(
        format='%H:%M',
        input_formats=['%H:%M', '%H-%M']
    )



    class Meta:
        model = models.Restaurant
        fields = ('id', 'name', 'address', 'phone', 'is_active', 'start_time', 'end_time')

        

class CategoryListSerializer(ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'restaurant', 'name', 'order_index')
        read_only_fields = ('restaurant',)
        

class CategoryEditSerializer(ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'restaurant', 'name', 'order_index')
        read_only_fields = ('restaurant', 'order_index')
        

class DishCreateSerializer(ModelSerializer):
    class Meta:
        model = models.Dish
        fields = ('id', 'category', 'name', 'price', 'is_available', 'description')
        read_only_fields = ('category', 'description')


class DishListSerializer(ModelSerializer):
    class Meta:
        model = models.Dish
        fields = ('id', 'category', 'name', 'price', 'is_available', 'description')
        read_only_fields = ('category', )


class DishDetailSerializer(ModelSerializer):
    class Meta:
        model = models.Dish
        fields = ('id', 'category', 'name', 'price', 'is_available', 'description', 'recept_items')
        read_only_fields = ('category', 'recept-items')


class DishStopResponseSerializer(ModelSerializer):
    class Meta:
        model = models.Dish
        fields = ('id', 'category', 'name', 'price', 'is_available', 'description', 'recept_items')

class DishStoplistSerializer(ModelSerializer):
    class Meta:
        model = models.Dish
        fields = ('category', 'name', 'is_available')
        read_only_fields = ('category', 'name')
        


class TableListSerializer(ModelSerializer):
    class Meta:
        model = models.Table
        fields = ('id', 'restaurant', 'number', 'seats', 'status')
        read_only_fields = ('restaurant',)


class TableBookSerializer(ModelSerializer):
    class Meta:
        model = models.Table
        fields = ('restaurant', 'number', 'guess_count', 'status')
        read_only_fields = ('restaurant', 'guess_count', 'number')



class ReceptItemSerializer(ModelSerializer):
    class Meta:
        model = models.ReceptItem
        fields = ('id', 'dish', 'ingredient', 'quantity_per_serving', 'unit')
        read_only_fields = ('dish', )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('restaurant', 'id', 'name', 'current_stock', 'unit', 'min_stock')
        read_only_fields = ('restaurant',)


class IngredientDetailSerializer(ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ('restaurant', 'id', 'name', 'current_stock', 'unit', 'min_stock')
        read_only_fields = ('restaurant', 'name', 'current_stock')



class IngredientAddSerializer(ModelSerializer):
    quantity = DecimalField(max_digits=10, decimal_places=2, required=True, write_only=True)

    class Meta:
        model = models.Ingredient
        fields = ('quantity',)
        read_only_fields = ('name', 'current_stock','unit')

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError("Mugdar 0 den kishi bolmawi kerek!")
        return value


class IngredientSubtractSerializer(ModelSerializer):
    quantity = DecimalField(max_digits=10, decimal_places=2, required=True, write_only=True)
    reason = CharField(required=True, write_only=True)

    class Meta:
        model = models.Ingredient
        fields = ('quantity', 'reason')

    def validate_quantity(self, value):
        if value <=0:
            raise ValidationError("Mugdar 0 den kishi bolmawi kerek!")
        elif self.instance and value > self.instance.current_stock:
            raise ValidationError("Skladta barinan artiq bolip ketti!")

        return value

        

class StockTransationSerializer(ModelSerializer):
    class Meta:
        model = models.StockTransaction
        fields = '__all__'




class MenuSerializer(ModelSerializer):
    dishes = DishListSerializer(read_only=True, many=True)
    class Meta:
        model = models.Category
        fields = ('id', 'restaurant', 'name', 'order_index', 'dishes')