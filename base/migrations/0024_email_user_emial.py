# Generated by Django 5.0.3 on 2024-03-20 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_campaign_created_at_campaign_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='user_emial',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
