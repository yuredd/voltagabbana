# Generated by Django 2.0.1 on 2018-03-07 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_remove_politician_present'),
    ]

    operations = [
        migrations.AddField(
            model_name='politician',
            name='present',
            field=models.BooleanField(default=False),
        ),
    ]