# Generated by Django 3.2.6 on 2022-12-05 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linefunc', '0012_order_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(default=0)),
                ('number', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(default='', max_length=255, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='image/')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='point',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
