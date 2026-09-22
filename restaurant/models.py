from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta


class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name='Restoran Ati')
    address = models.CharField(max_length=150, verbose_name='Manzili')
    phone = models.CharField(max_length=13, verbose_name="Telefon nomeri")
    # logo = models.ImageField(verbose_name="Restoran logosi", upload_to="C:\\Users\\Acer-pc\\Pictures\\Camera Roll\\psg.png",null=True, blank=True),

    is_active = models.BooleanField(default=True, verbose_name='Aktiv/Aktiv emes')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Kategoriya ati")
    order_index = models.CharField(max_length=3, verbose_name="Tartip nomeri")
    restoran = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=80, verbose_name='Tagam Ati')
    description = models.TextField(null=True, blank=True, verbose_name="Tariypi")
    price = models.DecimalField(verbose_name="Bahasi", max_digits=10, decimal_places=2)
    # photo = models.ImageField()
    is_available = models.BooleanField(default=False, verbose_name="Qol jetimliligi")

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="dishes")

    def __str__(self):
        return self.name


class Table(models.Model):
    STATUS = (
        ("bos", 'Bos'),
        ("bant", "Bant")
    )
    number = models.IntegerField(verbose_name="Stol nomeri", default=None)
    guess_count = models.IntegerField(verbose_name="Orin sani")
    status = models.CharField(max_length=20, choices=STATUS, verbose_name="Halati") # Choices
    # place = models.CharField(choices=PLACES, verbose_name="jaylasqan orni", null=)

    restoran = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')


    @property
    def current_status(self):
        now = timezone.now()
        current_date = now.date()
        current_time = now.time()

        # Hozirgi vaqtda ushbu stolda aktiv bron bor-yo'qligini tekshiramiz
        # (reservation_date va reservation_time + duration_hours oralig'ida)
        active_reservations = self.reservations.filter(
            reservation_date=current_date,
            status__in=['jaratildi', 'tastiqlandi']
        )

        for res in active_reservations:
            start_dt = datetime.combine(res.reservation_date, res.reservation_time)
            end_dt = start_dt + timedelta(hours=float(res.duration_hours))
            
            # Agar hozirgi vaqt bron vaqti oralig'ida bo'lsa
            if start_dt <= now <= end_dt:
                return 'band'
                
        return 'bos'

    def __str__(self):
        return f"{self.number} nomerli stol --> {self.guess_count} orinliq"



class ReceptItem(models.Model):

    UNIT = (
        ('kg', "Kilogramm"),
        ('gr', 'gramm'),
        ('mg', 'milligramm'),
        ('l', 'litr'),
        ('ml', 'ml'),
        ('none', 'olshem birligi')
    )

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='recept_items')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.PROTECT, related_name='ingredient', null=True, blank=True)
    quantity_per_serving = models.DecimalField(max_digits=8, decimal_places=3, validators=[MinValueValidator(0.001)], verbose_name='Mugdari')
    unit = models.CharField(choices=UNIT, max_length=10, verbose_name='olshem birligi', default='none')

    class Meta:
        # Bir tagamda bir ingredient  tek 1 marte ko'rsetilsin
        unique_together = ("dish", "ingredient")
        verbose_name = "Retsept elementi"
        verbose_name_plural = "Retsept elementlari"

        
    def __str__(self):
        return f"{self.ingredient.name}"




class Ingredient(models.Model):
    UNITS = (
        ('kg', 'kilogramm'),
        ('l', 'litr')
    )

    name = models.CharField(verbose_name="Ingredient ati")
    unit = models.CharField(max_length=12, choices=UNITS, verbose_name='Olshem birligi')
    current_stock = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Mugdari", validators=[MinValueValidator(0)])
    restoran = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='ingredients')

    def __str__(self):
        return self.name



class StockTransaction(models.Model):
    TYPES = (
        ('in', "IN",),
        ('out', "OUT")
    )


    type = models.CharField(choices=TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='Mugdari')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='stock_transaction')

    def __str__(self):
        return f"{self.ingredient.name} ------ {self.quantity} -- {self.type}"