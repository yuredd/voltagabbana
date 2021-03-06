# Generated by Django 2.0.1 on 2018-03-07 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Politician',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('surname', models.CharField(max_length=150)),
                ('gender', models.CharField(max_length=10)),
                ('college', models.CharField(max_length=100)),
                ('group', models.CharField(max_length=150)),
                ('dateOfBirth', models.DateField()),
                ('dateUpdate', models.DateField()),
                ('placeOfBirth', models.CharField(max_length=150)),
            ],
        ),
    ]
