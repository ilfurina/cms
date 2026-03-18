from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from student.views import info as stu_info
from sys_admin.views import news_list
from teacher.views import info as tea_info
from sys_admin.models import News, Carousel


def welcome(request):
    carousel_items = Carousel.objects.filter(is_active=True).order_by('order')
    news_list = News.objects.all()[:5]  # 取前5条新闻

    return render(request, 'welcome.html', {'news_list': news_list,'carousel_items': carousel_items})

def info(request):
    user = request.user
    if user.user_type == 'student':
        return stu_info(request)
    elif user.user_type == 'teacher':
        return tea_info(request)
