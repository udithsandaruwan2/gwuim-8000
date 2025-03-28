from django.shortcuts import render, redirect
from .forms import EmployeeFileForm
from .utils import csv_reader

def importExport(request):
    page = 'csv_manager'
    page_title = 'CSV Manager'

    if request.method == 'POST' and request.FILES:
        form = EmployeeFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the form (which saves the file)
            file_path = form.instance.file.url  # Get the relative file URL
            csv_reader(file_path)  # Pass the relative URL to the CSV reader
            return redirect('csv_manager')  # Redirect to 'csv_manager' page after saving
    else:
        form = EmployeeFileForm()  # Initialize the form for GET request

    context = {
        'page': page,
        'page_title': page_title,
        'form': form
    }

    return render(request, 'csv_manager/import-export.html', context)
