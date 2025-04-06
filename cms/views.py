from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def welcome(request):
    return render(request, 'welcome.html')


