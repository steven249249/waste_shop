# Generated by Django 3.2.6 on 2022-12-08 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0018_store_food_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store_food',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
