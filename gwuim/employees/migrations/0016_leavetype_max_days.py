# Generated by Django 5.1.7 on 2025-03-24 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0015_alter_employee_leave_balance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavetype',
            name='max_days',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
