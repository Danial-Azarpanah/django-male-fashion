# Generated by Django 4.1.6 on 2023-02-12 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='phone',
            field=models.CharField(max_length=20),
        ),
    ]
