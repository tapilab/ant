# Generated by Django 4.2.9 on 2024-02-05 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='EntityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=255)),
                ('entity_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.entitytype')),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='RelationshipType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('symmetric', models.BooleanField(default=False)),
                ('source_entity_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_relationship_type_set', to='core.entitytype')),
                ('target_entity_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_relationship_type_set', to='core.entitytype')),
            ],
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=2048)),
                ('entity_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.entitytype')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.field')),
            ],
        ),
        migrations.DeleteModel(
            name='Greeting',
        ),
        migrations.AddField(
            model_name='relationship',
            name='relationship_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.relationshiptype'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='source_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_relationship_set', to='core.entity'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='target_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_relationship_set', to='core.entity'),
        ),
        migrations.AddField(
            model_name='entity',
            name='entity_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.entitytype'),
        ),
        migrations.AddField(
            model_name='entity',
            name='values',
            field=models.ManyToManyField(to='core.value'),
        ),
    ]
