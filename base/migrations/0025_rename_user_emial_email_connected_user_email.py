# Generated by Django 5.0.3 on 2024-03-20 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_email_user_emial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='email',
            old_name='user_emial',
            new_name='connected_user_email',
        ),
    ]
