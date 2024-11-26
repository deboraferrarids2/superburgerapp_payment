# models.py
from django.db import models

class Transaction(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20)
    amount = models.IntegerField()
    qrcode = models.CharField(max_length=1000, null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Transaction for Order ID: {self.order_id}'
