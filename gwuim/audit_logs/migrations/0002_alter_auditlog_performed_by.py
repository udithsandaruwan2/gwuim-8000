# Generated by Django 5.1.7 on 2025-03-14 05:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit_logs', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='performed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.profile'),
        ),
    ]
