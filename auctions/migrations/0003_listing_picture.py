# Generated by Django 4.1.5 on 2023-02-21 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_remove_bid_item_listing_current_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
