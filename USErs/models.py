from django.contrib.auth.models import User
from django.db import models
from restaurant.models import Restaurant

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customers')
    role = models.CharField(default='klient')

    def __str__(self):
        return self.user.username


class Xizmetker(models.Model):
    ROLES = (
        ('Officiant', 'officiant'),
        ('Aspaz', 'aspaz'),
        ('Sklad xizmetkeri', 'sklad xizmetkeri')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='xizmetkerler')
    role = models.CharField(choices=ROLES, verbose_name='Lawazimi')
    is_active = models.BooleanField(default=True, verbose_name="Aktivligi")

    restoran = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff')

    def __str__(self):
        return f"{self.user.username} {self.role}"





class RestoranAdminmodel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adminler')
    role = models.CharField(default='restoran admin')
    is_active = models.BooleanField(default=True, verbose_name="Aktivligi")

    restoran = models.OneToOneField(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} {self.role}"