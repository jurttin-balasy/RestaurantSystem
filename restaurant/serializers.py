from . import models
from rest_framework.serializers import (
    ModelSerializer, DecimalField, 
    ValidationError
)


class RestaurantListSerializer(ModelSerializer):
    class Meta:
        model = models.Restaurant
        fields = ('id', 'name', 'address', 'phone', 'is_active')


class CategoryListSerializer(ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'restoran', 'name', 'order_index')
        read_only_fields = ('restoran',)


class DishCreateSerializer(ModelSerializer):
    class Meta:
        model = models.Dish
        fields = ('id', 'category', 'name', 'price', 'is_available', 'description')
        read_only_fields = ('category', )


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



class DishStoplistSerializer(ModelSerializer):
    class Meta:
        model = models.Dish
        fields = ('category', 'name', 'is_available')
        read_only_fields = ('category', 'name')
        


class TableListSerializer(ModelSerializer):
    class Meta:
        model = models.Table
        fields = ('id', 'restoran', 'number', 'guess_count', 'status')
        read_only_fields = ('restoran',)


class TableBookSerializer(ModelSerializer):
    class Meta:
        model = models.Table
        fields = ('restoran', 'number', 'guess_count', 'status')
        read_only_fields = ('restoran', 'guess_count', 'number')



class ReceptItemSerializer(ModelSerializer):
    class Meta:
        model = models.ReceptItem
        fields = ('id', 'dish', 'ingredient', 'quantity_per_serving', 'unit')
        read_only_fields = ('dish', )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ('restoran', 'id', 'name', 'current_stock', 'unit')
        read_only_fields = ('restoran',)


class IngredientDetailSerializer(ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ('restoran', 'id', 'name', 'current_stock', 'unit')
        read_only_fields = ('restoran', 'name', 'current_stock')



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




class StockTransationSerializer(ModelSerializer):
    class Meta:
        model = models.StockTransaction
        fields = '__all__'