# Generated by Django 4.1.6 on 2023-02-07 21:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_http_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="output",
            field=models.TextField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="scenario",
            name="body",
            field=models.JSONField(blank=True, help_text="HTTP body", null=True),
        ),
        migrations.AlterField(
            model_name="task",
            name="message",
            field=models.TextField(editable=False, null=True),
        ),
    ]
