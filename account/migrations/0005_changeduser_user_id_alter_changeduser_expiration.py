# Generated by Django 4.1.6 on 2023-02-28 15:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_changeduser_expiration'),
    ]

    operations = [
        migrations.AddField(
            model_name='changeduser',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='changeduser',
            name='expiration',
            field=models.DateTimeField(verbose_name=datetime.datetime(2023, 2, 28, 15, 48, 46, 868622, tzinfo=datetime.timezone.utc)),
        ),
    ]
