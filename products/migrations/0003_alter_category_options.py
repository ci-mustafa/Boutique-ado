# Generated by Django 5.1.3 on 2024-12-02 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_rename_reting_product_rating'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
    ]