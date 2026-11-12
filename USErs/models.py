from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from restaurant.models import Restaurant

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon nomer kiritiliwi shart!")
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo\'liwi kerek.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'liwi kerek.')

        return self.create_user(phone_number, password, **extra_fields)


# 2. CustomUser Modeli
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=13, unique=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Managerdi modelge biriktiremiz
    objects = CustomUserManager()


    USERNAME_FIELD = 'phone_number'  
    REQUIRED_FIELDS = []             

    def __str__(self):
        return self.phone_number






class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customers',error_messages={"unique": "Bu telefon nomer alleqashan dizimnen otken!"})
    role = models.CharField(default='customer')
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name='Email pochta')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Xizmetker(models.Model):
    ROLES = (
        ('waiter', 'waiter'),
        ('cook', 'cook'),
        ('storekeeper', 'storekeeper')
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='xizmetkerler')
    role = models.CharField(choices=ROLES, verbose_name='Lawazimi')
    is_active = models.BooleanField(default=True, verbose_name="Aktivligi")

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -- {self.role}"





class RestoranAdminmodel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='adminler')
    role = models.CharField(default='restaurant_admin')
    is_active = models.BooleanField(default=True, verbose_name="Aktivligi")
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='admin')


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}  -- {self.role}"