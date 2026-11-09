from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from restaurant.models import Table, Dish, Restaurant
from USErs.models import Xizmetker, Customer


class Order(models.Model):

    STATUS = (
        ('open', 'ashildi'),
        ('closed', 'jabildi')
    )

    PAYMEND_METHOD = (
        ('cash', 'naq pul'),
        ('card', 'palstik karta'),
        ('unset', 'belgisiz')
    )
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    waiter = models.ForeignKey(Xizmetker, verbose_name='Officiant', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, verbose_name='Statusi', choices=STATUS, default='open')
    payment_method =  models.CharField(max_length=20, choices=PAYMEND_METHOD, verbose_name="Tolem turi", default="unset")
    client = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    @property
    def total_order_price(self):
        """
        Buyirtpanin uliwma bahasi
        """
        return sum(item.total_price for item in self.order_items.all())

    def save(self, *args, **kwargs):
        if self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()

        if self.pk:
            order = Order.objects.filter(pk=self.pk).first()
            if order and order.status != "closed" and self.status == 'closed':
                if self.table:
                    self.table.status = 'free'
                    self.table.save(update_fields=['status'])

                    
        super().save(*args, **kwargs)

    def __str__(self):
        waiter_name = (
            f"{self.waiter.user.first_name} {self.waiter.user.last_name}".strip() or self.waiter.user.username
            if self.waiter  
            else "Officiant biriktirilmegen"
        )
        table_num = (
            f"Stol #{self.table.number}" if self.table else "Stolsiz buyurtpa"
        )

        return f"Order #{self.id} | {table_num} | {waiter_name}"


class OrderItem(models.Model):
    STATUS = (
        ('new', "jana"),
        ('sent', 'jiberildi'),
        ('cooking', 'tayyarlanip atir'),
        ("ready", "tayyar"),
        ('served', 'jetkizildi')
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Tagam")
    sent_at = models.DateTimeField(null=True, blank=True)

    note = models.TextField(null=True, blank=True, verbose_name="Qosimsha jaziw ushin")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Sani')
    status = models.CharField(max_length=50, verbose_name='Statusi', choices=STATUS, default="new")
  
    @property
    def total_price(self):
        if (self.dish and hasattr(self.dish, 'price') 
        and self.dish.price):
            return self.dish.price * self.quantity
        return 0

    @property
    def waiting_time_minutes(self):
        # Taom jiberilgan bo'lsa va hali tayyor/yetkazilgan bo'lmasa, vaqtni hisoblaydi
        if self.sent_at and self.status in ['sent', 'cooking']:
            delta = timezone.now() - self.sent_at
            return int(delta.total_seconds() // 60)
        return 0


    
    def __str__(self):
        table_num = (
            self.order.table.number
            if self.order and self.order.table
            else "Stolsiz"
        )

        dish_name = self.dish.name if self.dish else "Tagam tanlanbagan!"
        return f"{table_num} {dish_name} X {self.quantity} {self.get_status_display()}"