from django.http import JsonResponse
from django.shortcuts import render,redirect
import string
import random
from django.core.mail import send_mail
from django.urls import reverse

from sys_admin.models import College
from .models import User
from .models import CaptchaModel
from django.views.decorators.http import require_http_methods
from .forms import RegisterForm, LoginForm
from django.contrib.auth import get_user_model,login,logout
from teacher.models import Teacher
from student.models import Student


# User = get_user_model()

@require_http_methods(['GET', 'POST'])
def mylogin(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            # user_type = form.cleaned_data.get('user_type')
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                login(request, user)
                if user.user_type == 'teacher':
                    return redirect('teacher:dashboard')
                if user.user_type == 'student':
                    return redirect('student:dashboard')
                if user.user_type == 'admin':
                    return redirect('admin:dashboard')

                if not remember:
                    # 如果没有选择记住我，则设置session过期时间为0
                    request.session.set_expiry(0)
                return redirect('/')
                # return JsonResponse({'code': 200,
                #                      'message': '登录成功',
                #                      "sessionid": request.session.session_key
                #                      })
            else:
                return render(request, 'login.html', context={'form': 'form'})
        else:
            return render(request, 'login.html', context={'form': 'form'})

def mylogout(request):
    logout(request)
    return redirect('/')


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_type = form.cleaned_data.get('user_type')

            college_name = form.cleaned_data.get('college')
            college = College.objects.get(college_name=college_name)

            school_id = form.cleaned_data.get('school_id')

            user =  User.objects.create_user(email=email, username=username, password=password, user_type=user_type)
            login(request, user)
            if user.user_type == 'teacher':
                Teacher.objects.create(teacher_id=school_id, name=user.username,college=college, user=user)
                return redirect('teacher:dashboard')
            if user.user_type == 'student':
                Student.objects.create(student_id=school_id, name=user.username,college=college,user = user)
                return redirect('student:dashboard')

        else:
            return render(request,'register.html', context={'form': form})


def send_email_captcha(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({"code": 400, "message": "邮箱不能为空"})
    # 生成验证码
    captcha = "".join(random.sample(string.digits, 4))
    # 存储到数据库
    CaptchaModel.objects.update_or_create(email=email, defaults={"captcha": captcha})  # 有就更新，没有就创建

    send_mail("注册验证码", message=f"您的验证码是:{captcha}", recipient_list=[email], from_email=None)
    return JsonResponse({"code": 200, "message": "验证码发送成功"})

