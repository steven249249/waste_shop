# Generated by Django 3.2.6 on 2022-12-10 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0028_auto_20221210_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='description',
            field=models.CharField(default='', max_length=255, null=True),
        ),
    ]