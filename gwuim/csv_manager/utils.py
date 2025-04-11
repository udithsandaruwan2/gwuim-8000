import csv
import os
from django.conf import settings
from employees.models import Employee
from departments.models import Department
def csv_reader(file_path):
    # Remove the '/media' part from the file path if it starts with '/media'
    if file_path.startswith('/media/'):
        file_path = file_path[len('/media/'):]

    # Construct the absolute file path using MEDIA_ROOT
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    # Ensure the file exists
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return

    # Open the CSV file and process it
    with open(full_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)

        for row in csv_reader:
            if not row:  # Skip empty rows
                continue

            row_data = dict(zip(header, row))

            # Skip rows with missing required fields
            if not row_data.get('Full Name') or not row_data.get('Employee Code'):
                print(f"Skipping row due to missing required fields: {row}")
                continue

            # Handle optional fields (set None for empty values)
            department = None
            if row_data.get('Department'):
                department, _ = Department.objects.get_or_create(code=row_data['Department'])

            # Ensure employee_code is valid before proceeding
            try:
                employee_code = int(row_data['Employee Code'])
            except (ValueError, TypeError):
                print(f"Invalid Employee Code: {row_data['Employee Code']}. Skipping row: {row}")
                continue

            # Try to fetch the employee if they already exist
            employee, created = Employee.objects.get_or_create(
                employee_code=employee_code,
                defaults={
                    'full_name': row_data['Full Name'],
                    'email': row_data.get('Email'),
                    'contact_number': row_data.get('Contact Number'),
                    'date_of_birth': row_data.get('Date of Birth'),
                    'gender': row_data.get('Gender').lower() if row_data.get('Gender') else None,
                    'address': row_data.get('Address'),
                    'date_of_joining': row_data.get('Date of Joining'),
                    'position': row_data.get('Position'),
                    'department': department
                }
            )

            # If the employee already exists, update their details
            if not created:
                employee.full_name = row_data['Full Name']
                employee.email = row_data.get('Email')
                employee.contact_number = row_data.get('Contact Number')
                employee.date_of_birth = row_data.get('Date of Birth')
                employee.gender = row_data.get('Gender').lower() if row_data.get('Gender') else None
                employee.address = row_data.get('Address')
                employee.date_of_joining = row_data.get('Date of Joining')
                employee.position = row_data.get('Position')
                employee.department = department

                employee.save()
                print(f"Updated employee details for {employee.full_name} (Employee Code: {employee_code})")
            else:
                print(f"Created new employee: {employee.full_name} (Employee Code: {employee_code})")

            
