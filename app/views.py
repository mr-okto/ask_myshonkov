from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator

from .forms import *

questions = [{'id': 0, 'title': f'question # {0}', 'votes': 544,
              'text': 'Листинг вопросов с пагинацией по 20 вопросов на странице. '
                      'Необходимо реализовать сортировку по дате добавления и рейтингу'
                      ' (2 вида сортировки). В шапке сайта находятся: логотип, поисковая'
                      ' строка (для быстрого поиска по заголовку и содержимому вопроса), '
                      'кнопка задать вопрос (доступна только авторизованным). '
                      'В правой части шапки - юзерблок. ',
              'answers_count': 10,
              'tags': ['tag1', 'tag2', 'tag3']},
             {'id': 1, 'title': f'question # {1}', 'votes': 2,
              'text': 'Для авторизованного пользователя юзерблок содержит его ник',
              'answers_count': 0,
              'tags': ['tag1', 'tag2']}]
questions *= 30


def paginate(request, objects):
    paginator = Paginator(objects, 10)
    page_ind = request.GET.get('page', 1)
    page = paginator.get_page(page_ind)
    return page


def index(request):
    return render(request, 'index.html', {
        'title': 'New questions',
        'switch_title': 'Hot questions',
        'switch_url': 'index',
        'questions': paginate(request, questions)
    })


# @login_required(login_url='/login')
def ask(request):
    form = AskForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            tags = form.cleaned_data.get('tags')
    else:
        form = AskForm()
    return render(request, 'ask.html', {'form': form})


def login(reqest):
    return HttpResponse('Login Page')


def question(request, qid):
    q = questions[qid]
    return render(request, 'question_preview.html', {'question': q})
