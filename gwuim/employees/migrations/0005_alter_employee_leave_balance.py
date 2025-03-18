# Generated by Django 5.1.7 on 2025-03-18 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_alter_employee_date_of_joining_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='leave_balance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, null=True),
        ),
    ]
