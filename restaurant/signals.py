# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from order.models import Order

# @receiver(post_save, sender=Order)
# def manage_table_status_on_order_save(sender, instance, created, **kwargs):
#     # 1. Yangi order ochilganda va stol bo'sh bo'lsa -> 'bant' qilish
#     if created and instance.table and instance.table.status == 'bos':
#         instance.table.status = 'bant'
#         instance.table.save()

#     # 2. Order yopilganda ('CL') shu stolga boshqa ochiq order qolmagan bo'lsa -> 'bos' qilish
#     if instance.status == 'CL' and instance.table:
#         active_orders = Order.objects.filter(table=instance.table).exclude(status='CL')
#         if not active_orders.exists():
#             instance.table.status = 'bos'
#             instance.table.save()