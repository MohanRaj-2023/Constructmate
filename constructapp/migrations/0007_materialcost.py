# Generated by Django 4.2.3 on 2024-09-01 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('constructapp', '0006_remove_qda_analysis_material'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_name', models.CharField(max_length=100)),
                ('cost_per_unit', models.FloatField()),
            ],
        ),
    ]
