# Generated by Django 5.0.2 on 2024-04-11 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_useredits_subtitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='useredits',
            name='contributors',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='useredits',
            name='subtitle',
            field=models.CharField(default='', max_length=255),
        ),
    ]