# Generated by Django 5.0.3 on 2024-03-14 09:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0005_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="email",
            name="email_working",
            field=models.BooleanField(default=False),
        ),
    ]
