from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse

from .forms import *
from .models import *

context = {
    'best_users': Profile.objects.get_top(10),
    'hot_tags': Tag.objects.get_top(20),
}


def redirect_next(request):
    link = request.POST.get('continue', request.GET.get('continue', ''))
    if not link or link[0] != '/':
        link = reverse('index')
    return redirect(link)


def paginate(request, objects, page_count, tagret=None):
    paginator = Paginator(objects, page_count)
    if tagret is not None:
        for i in paginator.page_range:
            if tagret in paginator.get_page(i).object_list:
                page = paginator.get_page(i)
                return page

    page_ind = request.GET.get('page', 1)
    page = paginator.get_page(page_ind)
    return page


def get_likes(objects, user):
    if user.is_authenticated:
        profile = user.profile
        likes_sign = [q.get_like_sign(profile) for q in objects]
    else:
        likes_sign = [0 for q in objects]
    return likes_sign


def index(request):
    questions = paginate(request, Question.objects.get_new(), 10)
    likes_sign = get_likes(questions, request.user)
    context['questions'] = zip(questions, likes_sign)
    context['title'] = 'New questions'
    context['switch_title'] = 'Hot questions'
    context['switch_url'] = 'hot'
    return render(request, 'index.html', context)


def hot_questions(request):
    questions = paginate(request, Question.objects.get_hot(), 10)
    likes_sign = get_likes(questions, request.user)
    context['questions'] = zip(questions, likes_sign)
    context['title'] = 'Hot questions'
    context['switch_title'] = 'New questions'
    context['switch_url'] = 'index'
    return render(request, 'index.html', context)


def tagged_questions(request, tag_name):
    questions = paginate(request, Question.objects.get_tagged(tag_name), 10)
    likes_sign = get_likes(questions, request.user)
    context['questions'] = zip(questions, likes_sign)
    context['title'] = f'#{tag_name}'
    context['switch_title'] = 'All questions'
    context['switch_url'] = 'index'
    return render(request, 'index.html', context)


def view_question(request, qid):
    question = get_object_or_404(Question, pk=qid)
    if request.user.is_authenticated and request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(question, request.user.profile)
            redir_url = f"{reverse('question', kwargs={'qid': qid})}?ans_id={answer.pk}#{answer.pk}"
            return redirect(redir_url)
    else:
        form = AnswerForm()

    ans_id = request.GET.get('ans_id', 0)
    answer_start = None
    if ans_id:
        try:
            answer_start = Answer.objects.get(pk=int(ans_id))
        except (TypeError, ObjectDoesNotExist):
            pass

    answers = paginate(request, question.answer_set.all(), 30, answer_start)
    likes_sign = get_likes(answers, request.user)

    context['question'] = question
    if request.user.is_authenticated:
        context['q_like_sign'] = question.get_like_sign(request.user.profile)
    else:
        context['q_like_sign'] = 0
    context['answers'] = zip(answers, likes_sign)
    context['form'] = form
    return render(request, 'question.html', context)


@login_required()
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(request.user.profile)
            return redirect(reverse('question', kwargs={'qid': question.pk}))
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

    if request.user.is_authenticated:
        return redirect_next(request)
    context['form'] = form
    return render(request, 'login.html', context)


def log_out(request):
    auth.logout(request)
    return redirect_next(request)


def register(request):
    if request.user.is_authenticated:
        return redirect_next(request)

    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save()
            auth.login(request, profile.user)
            return redirect_next(request)
    else:
        form = SignupForm()
    context['form'] = form
    return render(request, 'signup.html', context)


@login_required()
def profile_settings(request):
    initial = {'username': request.user.username,
               'email': request.user.email,
               'nickname': request.user.profile.nickname}
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES, initial=initial)
        if form.is_valid() and form.has_changed():
            profile = form.save(request.user.profile)
            auth.logout(request)
            auth.login(request, profile.user)
    else:
        form = ProfileSettingsForm(initial=initial)
    context['form'] = form
    return render(request, 'settings.html', context)

@login_required
def ajax_like(request):
    try:
        qid = int(request.POST.get('id', None))
    except TypeError:
        return JsonResponse(dict(), status=422)

    obj_type = request.POST.get('type', '')
    sign = request.POST.get('is_positive', '')
    if obj_type != 'question' and obj_type != 'answer':
        return JsonResponse(dict(), status=422)
    if sign != 'true' and sign != 'false':
        return JsonResponse(dict(), status=422)

    is_positive = (sign == 'true')
    if obj_type == 'question':
        object_class = Question
    elif obj_type == 'answer':
        object_class = Answer

    object_ = get_object_or_404(object_class, id=qid)
    rating = Like.objects.add_like(request.user.profile, object_, is_positive)
    return JsonResponse({
        'likes_count': rating,
    })


@login_required
def ajax_mark_correct(request):
    try:
        qid = int(request.POST.get('id', None))
    except TypeError:
        return JsonResponse(dict(), status=422)
    try:
        answer = Answer.objects.get(id=qid)
    except ObjectDoesNotExist:
        return JsonResponse(dict(), status=422)

    result = answer.set_right(request.user.profile)
    return JsonResponse({
        'is_correct': result,
    })
