# Generated by Django 5.1.7 on 2025-03-24 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0012_alter_monthlyleavesummary_total_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='total_days',
            field=models.DecimalField(blank=True, decimal_places=1, editable=False, max_digits=5, null=True),
        ),
    ]
