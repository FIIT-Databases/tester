# Generated by Django 4.2 on 2023-04-28 11:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_alter_taskrecord_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="scenario",
            name="priority",
            field=models.IntegerField(null=True),
        ),
    ]
