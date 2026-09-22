from django.db import  models

from restaurant.models import Restaurant, Table
from USErs.models import Customer, RestoranAdminmodel

class Reservation(models.Model):
    STATUS = (
        ('jaratildi', 'Jaratildi'),
        ('jawildi', 'Jawildi'),
        ('tastiyiqlandi', 'Tastiyiqlandi'),
        ('biykar_etildi', 'Biykar etiw')

    )
    restoran = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    client = models.ForeignKey(Customer,on_delete=models.CASCADE, related_name='reservations')

    created_at = models.DateTimeField(auto_now_add=True)
    guests_count = models.PositiveBigIntegerField(default=1)
    status = models.CharField(choices=STATUS, max_length=50, default='jaratildi')
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=3, decimal_places=1, default=0.5)

    def __str__(self):
        return f"{self.client} - {self.table} ({self.reservation_date} {self.reservation_time})"