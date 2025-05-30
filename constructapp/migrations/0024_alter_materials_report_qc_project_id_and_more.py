# Generated by Django 4.2.3 on 2024-09-05 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('constructapp', '0023_materials_report_qc_project_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materials_report_qc',
            name='project_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='project_details',
            name='Reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project_details',
            name='Status',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project_details',
            name='materials_report',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
