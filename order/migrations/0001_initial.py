# Generated by Django 3.2.13 on 2024-07-26 14:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import order.models.products


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_token', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('em aberto', 'em aberto'), ('recebido', 'recebido'), ('em preparacao', 'em preparacao'), ('pronto', 'pronto'), ('finalizado', 'finalizado'), ('cancelado', 'cancelado')], default='em aberto', max_length=20, verbose_name='status')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='atualizado em')),
                ('cpf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_auth.cpf', verbose_name='cpf')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400)),
                ('category', models.CharField(choices=[('bebida', 'bebida'), ('lanche', 'lanche'), ('sobremesa', 'sobremesa'), ('acompanhamento', 'acompanhamento')], max_length=40, verbose_name='categoria')),
                ('description', models.CharField(max_length=400)),
                ('size', models.CharField(blank=True, choices=[('pequeno', 'pequeno'), ('medio', 'medio'), ('grande', 'grande')], max_length=10, null=True, verbose_name='tamanho')),
                ('image', models.FileField(blank=True, null=True, upload_to=order.models.products.imageFileUpdload, verbose_name='imagem')),
                ('amount', models.IntegerField(default=0, help_text='em centavos', verbose_name='valor')),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('changes', models.TextField(blank=True, max_length=300, null=True, verbose_name='alteracoes')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.order', verbose_name='pedido')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.product', verbose_name='produto')),
            ],
            options={
                'verbose_name': 'Item do pedido',
                'verbose_name_plural': 'Itens do pedido',
            },
        ),
    ]
