# Generated by Django 5.0.2 on 2024-04-25 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_alter_useredits_contributors_alter_useredits_logourl_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='about',
            name='blurb',
            field=models.CharField(default='  ', max_length=255),
        ),
    ]
