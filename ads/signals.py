from .models import Ad
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Ad)
def index_ad(sender, instance, **kwargs):
    instance.indexing()
