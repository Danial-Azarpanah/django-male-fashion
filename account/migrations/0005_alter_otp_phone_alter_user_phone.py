# Generated by Django 4.1.6 on 2023-02-12 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_otp_phone_alter_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='phone',
            field=models.CharField(max_length=13),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=13, unique=True),
        ),
    ]
