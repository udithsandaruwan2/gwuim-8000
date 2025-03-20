from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee, LeaveType, LeaveRequest
from .utils import searchEmployees, paginateEmployees, get_yearly_leave , process_leave_data
from .forms import EmployeeForm
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML


@login_required(login_url='login')
def employees(request):
    page = 'employees'
    page_title = 'Employees'

    # Queries With pagination
    employees, search_query = searchEmployees(request)
    custom_range, employees = paginateEmployees(request, employees, 10)
    employee_form = EmployeeForm()

    #Handling POST request
    if request.method == 'POST':
        if request.POST.get('action') == 'addEmployee':
            employee_form = EmployeeForm(request.POST)
            if employee_form.is_valid():
                employee_form.save()
                return redirect('employees')

    context = {
        'page': page,
        'page_title': page_title,
        'employees': employees,
        'search_query': search_query,
        'custom_range': custom_range,
        'employee_form': employee_form,
    }
    return render(request, 'employees/employees.html', context)
def employeeIndetail(request, pk):
    page = 'employees'
    page_title = 'Employee Details'

    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    current_year = timezone.now().year
    employee = Employee.objects.get(uid=pk)
    profile = request.user.profile
    leave_types = LeaveType.objects.all()

    data = get_yearly_leave(employee, 2025)
    print(data)


    leave_data = process_leave_data(data)
    print(leave_data)
    

    #Handling POST request
    if request.method == 'POST':
        if request.POST.get('action') == 'addLeaveRequest':
            request_type = request.POST.get('requestType')
            leave_type = LeaveType.objects.get(uid=request.POST.get('leaveType'))
            start_date = timezone.datetime.strptime(request.POST.get('startDate'), '%Y-%m-%d').date()
            comming_date = timezone.datetime.strptime(request.POST.get('commingDate'), '%Y-%m-%d').date()
            reason = request.POST.get('reason')
            status = request.POST.get('status')
            LeaveRequest.objects.create(
                employee = employee,
                systemized_by=profile,
                reason=reason,
                status=status,
                leave_type=leave_type,
                start_date=start_date,
                coming_date=comming_date,
                request_type=request_type,
            )
        return redirect('employee-indetail', pk=pk)

    context = {
        'page': page,
        'page_title': page_title,
        'pk': pk,
        'current_year': current_year,
        'employee': employee,
        'profile': profile,
        'leave_types': leave_types,
        'months': months,
        'leave_data': leave_data,
    }

    return render(request, 'employees/employee-indetail.html', context)




def downloadReport(request, pk):
    try:
        # Fetch employee details based on the pk (primary key)
        employee = Employee.objects.get(pk=pk)
        
        # Prepare data to pass into the template
        current_year = timezone.now().year
        
        context = {
            'pk': pk,
            'current_year': current_year,
            'employee': employee,
            'page': 'employee_report',
            'page_title': 'Leave Report for {}'.format(employee.full_name),
            'request': request,  # Pass the request to generate absolute URLs
        }
        
        # Render the HTML content with context
        html_content = render_to_string('employees/employee-indetail.html', context)

        # Create the PDF with WeasyPrint (A4 landscape layout)
        pdf = HTML(string=html_content).write_pdf(
            stylesheets=[
                'static/theme_dashboard/assets/css/styles.css',  # Ensure the CSS path is correct
            ],
            presentational_hints=True,
            options={'page-size': 'A4', 'orientation': 'landscape'}
        )

        # Return the PDF as a response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=leave_report_{pk}.pdf'
        return response
    except Employee.DoesNotExist:
        # Handle the case where the employee with the given pk does not exist
        return HttpResponse("Employee not found.", status=404)

def leaveTypes(request):
    page = 'leave_types'
    page_title = 'Leave Types'

    if request.method == 'POST':
        if request.POST.get('action') == 'addLeaveType':
            code = request.POST.get('leaveTypeCode')
            name = request.POST.get('leaveTypeName')
            description = request.POST.get('leaveTypeDescription')
            LeaveType.objects.create(code=code, name=name, description=description)

    leave_types = LeaveType.objects.all()

    context = {
        'page': page,
        'page_title': page_title,
        'leave_types': leave_types,
    }

    return render(request, 'employees/leave-types.html', context)