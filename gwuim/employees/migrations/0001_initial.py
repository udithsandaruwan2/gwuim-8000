# Generated by Django 5.1.7 on 2025-03-14 03:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('departments', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('uid', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('employee_code', models.IntegerField(blank=True, null=True)),
                ('full_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('contact_number', models.CharField(blank=True, max_length=20, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('date_of_joining', models.DateField()),
                ('date_of_leaving', models.DateField(blank=True, null=True)),
                ('leave_balance', models.JSONField(default=dict)),
                ('position', models.CharField(blank=True, max_length=255, null=True)),
                ('uid', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='departments.department')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('request_type', models.CharField(choices=[('half', 'Half Day'), ('full', 'Full Day')], default='full', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending', max_length=10)),
                ('reason', models.TextField(blank=True, null=True)),
                ('uid', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('systemized_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.profile')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.leavetype')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveAdjustment',
            fields=[
                ('adjustment_amount', models.IntegerField()),
                ('reason', models.TextField()),
                ('uid', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('leave_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.leaverequest')),
            ],
        ),
    ]
