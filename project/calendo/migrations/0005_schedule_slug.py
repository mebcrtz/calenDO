# Generated by Django 5.1.4 on 2024-12-14 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendo', '0004_dayofweek_item_itemoccurrence_schedule_item_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
