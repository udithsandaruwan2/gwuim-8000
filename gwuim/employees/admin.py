from django.contrib import admin
from .models import Employee, LeaveAdjustment, LeaveRequest, LeaveType, MonthlyLeaveSummary, Designation

admin.site.register(Employee)
admin.site.register(LeaveAdjustment)
admin.site.register(LeaveRequest)
admin.site.register(LeaveType)
admin.site.register(MonthlyLeaveSummary)
admin.site.register(Designation)