# Generated by Django 3.2.6 on 2022-12-10 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0025_order_user_get'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='value',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
