from django.shortcuts import render

def classlist(request):

    return render(request, 'classes/classlist.html')
