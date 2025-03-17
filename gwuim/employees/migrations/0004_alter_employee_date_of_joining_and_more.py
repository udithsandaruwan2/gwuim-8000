# Generated by Django 5.1.7 on 2025-03-17 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='date_of_joining',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='leave_balance',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
