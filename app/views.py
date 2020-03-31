from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator
from django.urls import reverse

from .forms import *
from .models import *

context = {
    'best_users': Profile.objects.get_top(10),
    'hot_tags': Tag.objects.get_top(20),
}


def redirect_next(request):
    link = request.POST.get('next', request.GET.get('next', ''))
    if not link:
        link = reverse('index')
    return redirect(link)


def paginate(request, objects, page_count):
    paginator = Paginator(objects, page_count)
    page_ind = request.GET.get('page', 1)
    page = paginator.get_page(page_ind)
    return page


def index(request):
    context['title'] = 'New questions'
    context['switch_title'] = 'Hot questions'
    context['switch_url'] = 'hot'
    context['questions'] = paginate(request, Question.objects.get_new(), 10)
    return render(request, 'index.html', context)


def hot(request):
    context['title'] = 'Hot questions'
    context['switch_title'] = 'New questions'
    context['switch_url'] = 'index'
    context['questions'] = paginate(request, Question.objects.get_hot(), 10)
    return render(request, 'index.html', context)


def tagged(request, tag_name):
    context['title'] = f'#{tag_name}'
    context['switch_title'] = 'All questions'
    context['switch_url'] = 'index'
    context['questions'] = paginate(request, Question.objects.get_tagged(tag_name), 10)
    return render(request, 'index.html', context)


@login_required()
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            tags = form.cleaned_data.get('tags')
    else:
        form = AskForm()
    context['form'] = form
    return render(request, 'ask.html', context)


def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data.get('login'),
                                     password=form.cleaned_data.get('password'))
            if user:
                auth.login(request, user)
                return redirect_next(request)
            else:
                form.add_error('password', 'Login and password do not match')
    else:
        form = LoginForm()
    context['form'] = form
    return render(request, 'login.html', context)


def log_out(request):
    auth.logout(request)
    return redirect_next(request)


def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            nickname = form.cleaned_data.get('nickname')
            password = form.cleaned_data.get('password')
            avatar = form.cleaned_data.get('avatar')
            profile = Profile.objects.create_profile(
                username=username, email=email, nickname=nickname,
                password=password, avatar=avatar)

            auth.login(request, profile.user)
            return redirect_next(request)
    else:
        form = SignupForm()
    context['form'] = form
    return render(request, 'signup.html', context)


def question(request, qid):
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get('text')
    else:
        form = AnswerForm()
    q = get_object_or_404(Question, pk=qid)
    context['question'] = q
    context['answers'] = paginate(request, q.answer_set.all(), 30)
    context['form'] = form
    return render(request, 'question.html', context)


@login_required()
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES)
        if form.is_valid():
            new_login = form.cleaned_data.get('login')
    else:
        form = ProfileSettingsForm()
        form.fields['login'].initial = 'Dr. Pepper'
        form.fields['email'].initial = 'drpepper@mail.ru'
        form.fields['nickname'].initial = 'Dr. Pepper'

    context['form'] = form
    return render(request, 'settings.html', context)
