from django.shortcuts import render, redirect
from .forms import EmployeeFileForm

def importExport(request):
    page = 'csv_manager'
    page_title = 'CSV Manager'

    form = EmployeeFileForm()

    if request.method == 'POST' and request.FILES:
        form = EmployeeFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('csv_manager')  # Redirect to a list of employees or another page
    else:
        form = EmployeeFileForm()

    context = {
        'page':page,
        'page_title':page_title, 
        'form': form
    }
    return render(request, 'csv_manager/import-export.html', context)