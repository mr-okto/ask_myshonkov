from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator

from .forms import *

answers = [{'pk': 1, 'votes': 5, 'author': 'Nobody', 'correct': True,
           'text': 'Автор вопроса может пометить один из ответов как правильный.'
                   ' Пользователи могут голосовать за вопросы и ответы с помощью '
                   'лайков. '},
           {'pk': 2, 'votes': 2, 'author': 'Noone', 'correct': False,
            'text': 'This works because returning false from the click event'
                    ' stops the chain of execution continuing.'}]

questions = [{'id': 0, 'title': f'question # {0}', 'votes': 544, 'author': 'Guest',
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
    return render(request, 'index.html', {
        'title': 'New questions',
        'switch_title': 'Hot questions',
        'switch_url': 'index',
        'questions': paginate(request, questions, 10)
    })


# @login_required()
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            tags = form.cleaned_data.get('tags')
    else:
        form = AskForm()
    return render(request, 'ask.html', {'form': form})


def login(request):
    return HttpResponse('Login Page')


def question(request, qid):

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data.get('text')
    else:
        form = AnswerForm()

    q = questions[qid]
    ans = paginate(request, answers, 30)
    return render(request, 'question.html',
                  {'question': q, 'answers': ans, 'form': form})
