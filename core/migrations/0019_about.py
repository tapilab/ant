# Generated by Django 5.0.2 on 2024-04-16 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_useredits_contributors_alter_useredits_subtitle'),
    ]

    operations = [
        migrations.CreateModel(
            name='About',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blurb', models.CharField(default='Welcome', max_length=500)),
            ],
        ),
    ]