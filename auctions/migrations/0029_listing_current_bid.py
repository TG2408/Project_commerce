# Generated by Django 3.1.7 on 2021-05-30 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0028_auto_20210530_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_bid',
            field=models.ImageField(default=0, upload_to=''),
        ),
    ]
