from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import searchRequests, paginateRequests


@login_required(login_url='login')
def leaveRequets(request):
    page = 'leave_requests'
    page_title = 'Leave Requests'

    # Queries With pagination
    requests, search_query = searchRequests(request)
    custom_range, requests = paginateRequests(request, requests, 10)

    context = {
        'page': page,
        'page_title': page_title,
        'requests': requests,
        'search_query': search_query,
        'custom_range': custom_range,
        'requests':requests
    }
    return render(request, 'leave_management/leave_requests.html', context)