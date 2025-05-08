from django.shortcuts import render, redirect
from .models import College, Major, News
from django.core.files.base import ContentFile
from .models import Carousel


def dashboard(request):

    return render(request, 'admin/dashboard.html')

def college_list(request):
    colleges = College.objects.all()
    return render(request, 'admin/college_list.html', {'colleges': colleges})

def create_college(request):
    if request.method == 'POST':
        college_id = request.POST.get('college_id')
        college_name = request.POST.get('name')
        college = College.objects.create(college_id=college_id, college_name=college_name)
        return redirect('admin:college_list')


def major_list(request, college_id):
    college = College.objects.get(college_id=college_id)
    majors = Major.objects.filter(college_id=college_id)
    return render(request, 'admin/major_list.html', {'majors': majors, 'college': college})

def create_major(request):
    if request.method == 'POST':
        college_id = request.POST.get('college_id')
        major_id = request.POST.get('major_id')
        major_name = request.POST.get('name')
        college = College.objects.get(college_id=college_id)
        major = Major.objects.create(college=college, major_id=major_id, major_name=major_name)
        return redirect('admin:major_list',college_id=college_id)

def news_list(request):
    news_list = News.objects.all()
    return render(request, 'admin/news_list.html', {'news_list': news_list})

def news_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        file = News()
        file.news_file.save(name=title, content=ContentFile(content),save=True)

        file.title = title
        file.save()

        return redirect('admin:news_list')
    return render(request, 'admin/news_create.html')

def  news_delete(request, news_id):
    news = News.objects.get(id=news_id)
    news.news_file.delete()
    news.delete()
    return redirect('admin:news_list')

def news_edit(request, news_id):
    news = News.objects.get(id=news_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        file = news.news_file
        file.save(name=title, content=ContentFile(content),save=True)
        news.title = title
        news.save()
        return redirect('admin:news_list')

def news_detail(request, news_id):
    news = News.objects.get(id=news_id)
    with news.news_file.open(mode='r') as f:
        news_content = f.read()
    return render(request, 'admin/news.html', {'news': news,  'news_content': news_content})

def carousel_list(request):
    carousels = Carousel.objects.filter(is_active=True).order_by('order')
    return render(request, 'admin/carousel_list.html', {'carousels': carousels})


def create_carousel(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        link_url = request.POST.get('link_url')
        order = request.POST.get('order', 0)
        is_active = 'is_active' in request.POST

        Carousel.objects.create(
            title=title,
            image=image,
            link_url=link_url,
            order=order,
            is_active=is_active
        )
        return redirect('admin:carousel_list')
    return render(request, 'admin/create_carousel.html')

def delete_carousel(request, carousel_id):
    carousel = Carousel.objects.get(id=carousel_id)
    carousel.image.delete()  # 删除图片文件
    carousel.delete()
    return redirect('admin:carousel_list')

