# Generated by Django 4.1.7 on 2023-03-03 15:32

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_task_additional_information_alter_evaluation_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignment",
            name="schemas",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100), blank=True, null=True, size=None
            ),
        ),
    ]
