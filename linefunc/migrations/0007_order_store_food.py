# Generated by Django 3.2.6 on 2022-10-13 05:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0006_auto_20221013_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='store_food',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='linefunc.store_food'),
        ),
    ]