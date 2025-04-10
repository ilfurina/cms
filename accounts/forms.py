from os.path import exists
from .models import User
from django import forms
# from django.contrib.auth import get_user_model

# User = get_user_model()

from myauth.models import CaptchaModel


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=3, error_messages={
        'required': '用户名不能为空',
        'max_length': '用户名不能超过20个字符',
        'min_length': '用户名不能少于3个字符',
    })
    email = forms.EmailField(error_messages={
        'required': '邮箱不能为空',
        'invalid': '邮箱格式不正确',
    })
    captcha =  forms.CharField(max_length=4, min_length=4, error_messages={
        'required': '验证码不能为空',
        'max_length': '验证码不能超过4个字符',
        'min_length': '验证码不能少于4个字符',
    })
    password = forms.CharField(max_length=20, min_length=6, error_messages={
        'required': '密码不能为空',
        'max_length': '密码不能超过20个字符',
        'min_length': '密码不能少于6个字符',
    })
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect
        )
    college = forms.CharField(max_length=20, min_length=3, error_messages={
        'required': '学院不能为空',
        'max_length': '学院不能超过20个字符',
        'min_length': '学院不能少于3个字符',
    })
    school_id = forms.CharField(max_length=20, min_length=3, error_messages={
        'required': '学号不能为空',
        'max_length': '学号不能超过20个字符',
        'min_length': '学号不能少于3个字符',
    })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exists = User.objects.filter(email=email).exists()
        if exists:
            raise forms.ValidationError('邮箱已注册！')
        return email

    def clean_captcha(self):
        captcha = self.cleaned_data.get('captcha')
        email = self.cleaned_data.get('email')
        captcha_model = CaptchaModel.objects.filter(email=email, captcha=captcha).first()
        if not captcha_model:
            raise forms.ValidationError('验证码错误！')
        captcha_model.delete()
        return captcha

class LoginForm(forms.Form):
    email = forms.EmailField(error_messages={
        'required': '邮箱不能为空',
        'invalid': '邮箱格式不正确',
    })
    password = forms.CharField(max_length=20, min_length=6, error_messages={
        'required': '密码不能为空',
        'max_length': '密码不能超过20个字符',
        'min_length': '密码不能少于6个字符',
    })
    remember = forms.IntegerField(required= False)
