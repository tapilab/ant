# Generated by Django 4.2.9 on 2024-02-28 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_entitytype_color_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='end_date',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='entity',
            name='start_date',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
