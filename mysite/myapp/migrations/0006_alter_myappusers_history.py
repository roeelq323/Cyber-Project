# Generated by Django 5.0.2 on 2024-02-29 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_myappusers_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myappusers',
            name='history',
            field=models.IntegerField(default=0),
        ),
    ]