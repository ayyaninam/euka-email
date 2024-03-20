# Generated by Django 5.0.3 on 2024-03-15 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_campaign_to_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='status',
            field=models.CharField(choices=[('Dead', 'Dead'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Dead', max_length=20),
            preserve_default=False,
        ),
    ]
