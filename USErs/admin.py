from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'first_name', 'last_name', 'email')

    search_fields = ('phone_number', 'first_name', 'last_name')
