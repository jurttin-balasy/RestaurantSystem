# # signals.py
# from django.db.models.signals import post_delete
# from django.dispatch import receiver
# from .models import Xizmetker

# @receiver(post_delete, sender=Xizmetker)
# def delete_related_user(sender, instance, **kwargs):
#     if instance.user:
#         instance.user.delete()