# Generated by Django 4.2.2 on 2023-08-01 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='content',
            new_name='prompt',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='title',
            new_name='role',
        ),
    ]