# Generated by Django 3.2.6 on 2022-12-08 23:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0021_rename_end_time_store_food_end_order_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='time',
            new_name='order_time',
        ),
    ]
