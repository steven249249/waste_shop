# Generated by Django 3.2.6 on 2022-12-09 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0023_order_paied'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='paied',
            new_name='paid',
        ),
    ]
