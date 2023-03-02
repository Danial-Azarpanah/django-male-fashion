# Generated by Django 4.1.6 on 2023-02-28 04:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_emailchangeduser_delete_emailchangeotp'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=11)),
                ('email', models.CharField(max_length=100)),
                ('code', models.CharField(blank=True, max_length=6, null=True)),
                ('token', models.CharField(max_length=300)),
                ('expiration', models.DateTimeField(verbose_name=datetime.datetime(2023, 2, 28, 4, 29, 47, 92752, tzinfo=datetime.timezone.utc))),
            ],
            options={
                'verbose_name': 'email change otp code',
            },
        ),
        migrations.DeleteModel(
            name='EmailChangedUser',
        ),
    ]
