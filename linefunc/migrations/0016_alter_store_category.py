# Generated by Django 3.2.6 on 2022-12-06 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0015_alter_store_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='category',
            field=models.CharField(choices=[('bread', 'bread'), ('bento', 'bento')], default='bread', max_length=255),
        ),
    ]