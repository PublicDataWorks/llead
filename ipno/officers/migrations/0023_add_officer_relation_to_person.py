# Generated by Django 3.1.4 on 2021-11-04 05:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_create_model_person'),
        ('officers', '0022_alter_event_department_uof_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='officers', to='people.person'),
        ),
    ]
