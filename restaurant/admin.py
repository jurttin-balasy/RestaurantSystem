from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'address', 'is_active')

    search_fields = ('name',)

    list_filter = ('is_active',)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant', 'order_index')
    search_fields = ('name', 'order_index')
    list_filter = ('restaurant', )




@admin.register(models.Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category_id', 'is_available')
    search_fields = ('name', 'price')
    list_filter = ('is_available',)



@admin.register(models.Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'seats')

    search_fields = ('number',)

    list_filter = ('seats',)


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'current_stock', 'restaurant')

    search_fields = ('name', )

    list_filter = ('restaurant',)



@admin.register(models.StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient_id', 'reason', 'created_at')

    list_filter = ('created_at', 'ingredient_id')