# Generated by Django 4.2.5 on 2023-09-28 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='zipcode',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
