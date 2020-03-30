from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator

from .forms import *

context = {
    'best_users': ['John Doe', 'Mr. Freeman', 'Bender'],
    'hot_tags': ['perl', 'python', 'TechnoPark', 'MySQL', 'django', 'MailRu', 'Chrome', 'Firefox',
                 'Bootstrap', 'Twitter', 'ICQ'],
}

answers = [{'pk': 1, 'votes': 5, 'author': 'NoNameFella', 'correct': True,
           'text': 'Автор вопроса может пометить один из ответов как правильный.'
                   ' Пользователи могут голосовать за вопросы и ответы с помощью '
                   'лайков. В файле base.html нужно создать основную верстку (любой)'
                   ' страницы. Для упрощения задачи нужно скачать и использовать CSS '
                   'библиотеку Twitter Bootstrap. Файлы (как свои CSS стили, так и файлы Bootstrap)'
                   ' нужно разместить в директории static'},
           {'pk': 2, 'votes': 2, 'author': 'Noone', 'correct': False,
            'text': 'This works because returning false from the click event'
                    ' stops the chain of execution continuing.'}]

questions = [{'id': 0, 'title': f'question # {0}', 'votes': 544, 'author': 'NamedFella',
              'text': 'Листинг вопросов с пагинацией по 20 вопросов на странице. '
                      'Необходимо реализовать сортировку по дате добавления и рейтингу'
                      ' (2 вида сортировки). В шапке сайта находятся: логотип, поисковая'
                      ' строка (для быстрого поиска по заголовку и содержимому вопроса), '
                      'кнопка задать вопрос (доступна только авторизованным). '
                      'В правой части шапки - юзерблок. ',
              'answers_count': 35,
              'tags': ['tag1', 'tag2', 'tag3']},
             {'id': 1, 'title': f'question # {1}', 'votes': 2, 'author': 'Kotk',
              'text': 'Для авторизованного пользователя юзерблок содержит его ник',
              'answers_count': 3,
              'tags': ['tag1', 'tag2']}]

questions *= 30


def paginate(request, objects, page_count):
    paginator = Paginator(objects, page_count)
    page_ind = request.GET.get('page', 1)
    page = paginator.get_page(page_ind)
    return page


def index(request):
    context['title'] = 'New questions'
    context['switch_title'] = 'Hot questions'
    context['switch_url'] = 'hot'
    context['questions'] = paginate(request, questions, 10)
    return render(request, 'index.html', context)


def hot(request):
    context['title'] = 'Hot questions'
    context['switch_title'] = 'New questions'
    context['switch_url'] = 'index'
    context['questions'] = paginate(request, questions, 10)
    return render(request, 'index.html', context)


def tagged(request, tag):
    context['title'] = f'#{tag}'
    context['switch_title'] = 'All questions'
    context['switch_url'] = 'index'
    context['questions'] = paginate(request, questions, 10)
    return render(request, 'index.html', context)


# @login_required()
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            tags = form.cleaned_data.get('tags')
    else:
        form = AskForm()
    context['form'] = form
    return render(request, 'ask.html', context)


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_data = form.cleaned_data.get('login')
            form.add_error('password', 'Wrong password')
    else:
        form = LoginForm()
    context['form'] = form
    return render(request, 'login.html', context)


def logout(request):
    redirect_link = request.GET.get('next', '/')
    return redirect(redirect_link)


def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            login_data = form.cleaned_data.get('login')
            form.add_error('email', 'Email already registered')
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

    context['question'] = questions[qid]
    context['answers'] = paginate(request, answers, 30)
    context['form'] = form
    return render(request, 'question.html', context)


# @login_required()
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST)
        if form.is_valid():
            new_login = form.cleaned_data.get('login')
    else:
        form = ProfileSettingsForm()
        form.fields['login'].initial = 'Dr. Pepper'
        form.fields['email'].initial = 'drpepper@mail.ru'
        form.fields['nickname'].initial = 'Dr. Pepper'

    context['form'] = form
    return render(request, 'settings.html', context)
