# Generated by Django 3.2.6 on 2022-11-16 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0011_order_user_now'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='description',
            field=models.CharField(default='', max_length=255, null=True),
        ),
    ]
