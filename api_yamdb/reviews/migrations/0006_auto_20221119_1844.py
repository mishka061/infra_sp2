# Generated by Django 2.2.16 on 2022-11-19 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20221119_1754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='title',
            options={'ordering': ['name'], 'verbose_name': 'Произведение', 'verbose_name_plural': 'Произведения'},
        ),
    ]