# Generated by Django 4.1.2 on 2022-10-19 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_order_delivery_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_status',
            field=models.CharField(choices=[('Waiting for payment', 'Waiting for payment'), ('Collecting order', 'Collecting order'), ('Sent', 'Sent')], default='Waiting for payment', max_length=100),
        ),
    ]
