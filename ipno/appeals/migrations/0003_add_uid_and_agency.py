# Generated by Django 3.1.13 on 2023-02-13 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appeals', '0002_remove_appealed'),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='agency',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='appeal',
            name='uid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
