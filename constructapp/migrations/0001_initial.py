# Generated by Django 4.2.3 on 2024-08-27 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='customer_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=50)),
                ('Contact', models.CharField(max_length=15)),
                ('Email', models.CharField(max_length=50)),
                ('Password', models.CharField(max_length=20)),
            ],
        ),
    ]
