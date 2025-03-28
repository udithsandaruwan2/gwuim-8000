from django.shortcuts import render

def importExport(request):
    page = 'csv_manager'
    page_title = 'CSV Manager'

    context = {
        'page':page,
        'page_title':page_title
    }
    return render(request, 'csv_manager/import-export.html', context)