# Generated by Django 5.1.7 on 2025-04-08 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_leaverequest_entering_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='full_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
