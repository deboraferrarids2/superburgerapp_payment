# Generated by Django 3.2.13 on 2024-12-02 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_transaction_external_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='order_id',
            field=models.CharField(max_length=50),
        ),
    ]
