# Generated by Django 3.2.6 on 2022-12-10 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0024_rename_paied_order_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='user_get',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
