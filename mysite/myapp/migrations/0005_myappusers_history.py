# Generated by Django 5.0.2 on 2024-02-29 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_remove_myappusers_password4'),
    ]

    operations = [
        migrations.AddField(
            model_name='myappusers',
            name='history',
            field=models.IntegerField(default=0, max_length=10),
        ),
    ]
