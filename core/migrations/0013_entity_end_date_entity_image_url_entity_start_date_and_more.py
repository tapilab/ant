# Generated by Django 4.2.9 on 2024-02-28 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_rename_graph_network'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='image_url',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='start_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='entitytype',
            name='end_date_field_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='entitytype',
            name='start_date_field_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
