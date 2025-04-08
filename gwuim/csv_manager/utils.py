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

            Employee.objects.create(
                employee_code=int(row_data['Employee Code']) if row_data['Employee Code'] else None,
                full_name=row_data['Full Name'],
                email=row_data['Email'] if row_data.get('Email') else None,
                contact_number=row_data['Contact Number'] if row_data.get('Contact Number') else None,
                date_of_birth=row_data['Date of Birth'] if row_data.get('Date of Birth') else None,
                gender=row_data['Gender'].lower() if row_data.get('Gender') else None,
                address=row_data['Address'] if row_data.get('Address') else None,
                date_of_joining=row_data['Date of Joining'] if row_data.get('Date of Joining') else None,
                position=row_data['Position'] if row_data.get('Position') else None,
                department=department
            )
            
