from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError, FieldError
from django.contrib.auth.models import User
from os import path


class ProfileManager(models.Manager):
    def username_exists(self, username):
        return User.objects.filter(username=username).exists()

    def nickname_exists(self, nickname):
        return self.filter(nickname=nickname).exists()

    def email_exists(self, email):
        return User.objects.filter(email=email).exists()

    def get_top(self, count):
        return self.order_by('-reputation')[:count]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30, unique=True)
    reputation = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='uploads',
                               default=path.join('uploads', 'avatar_placeholder.jpg'))
    objects = ProfileManager()

    def update_username(self, username):
        if Profile.objects.username_exists(username):
            return False
        self.user.username = username
        self.user.save()
        return True

    def update_nickname(self, nickname):
        if Profile.objects.nickname_exists(nickname):
            return False
        self.user.username = nickname
        self.user.save()
        return True

    def update_email(self, email):
        if Profile.objects.email_exists(email):
            return False
        self.user.email = email
        self.user.save()
        return True

    def update_reputation(self, rep_change):
        self.reputation += rep_change
        self.save()
        return True

    def update_avatar(self, avatar):
        if not avatar:
            avatar = self.avatar.default
        self.avatar = avatar
        self.save()
        return True

    def __str__(self):
        return self.nickname


class LikeManager(models.Manager):
    def add_like(self, author, content_object, is_positive):
        rating_delta = 1 if is_positive else (-1)
        likes = self.filter(author=author, content_object=content_object)
        if not likes:
            self.add(author=author, content_object=content_object, is_positive=is_positive)
            return rating_delta
        if not likes.filter(is_positive=is_positive).exists():
            # Flip sign
            likes.update(is_positive=is_positive)
            return rating_delta * 2
        else:
            # Like has already been set
            return 0


class Like(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_positive = models.BooleanField(default=True)

    objects = LikeManager()

    def __str__(self):
        return f'#{self.object_id} {self.author} ({self.is_positive})'


class TagManager(models.Manager):
    def get_top(self, quantity):
        top_tags = [{'tag': None, 'count': 0} for _ in range(quantity)]
        for tag in self.all():
            tag_count = Question.objects.filter(tags=tag).count()
            if top_tags[-1]['count'] < quantity:
                top_tags[-1]['tag'] = tag
                top_tags[-1]['count'] = tag_count
                top_tags.sort(key=lambda x: x['count'], reverse=True)

        result_clean = [x['tag'] for x in top_tags if x['tag'] is not None]
        return result_clean

    def get_or_create(self, name):
        return super().get_or_create(name=name.lower())


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    objects = TagManager()

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def get_new(self):
        return self.order_by('-creation_dt')

    def get_hot(self):
        return self.order_by('-rating')

    def get_tagged(self, tag_name):
        return self.filter(tags__name=tag_name)


class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    text = models.CharField(max_length=1000)
    tags = models.ManyToManyField(Tag, blank=True)
    creation_dt = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    is_open = models.BooleanField(default=True)

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def add_tags(self, tags):
        for tag in tags:
            self.tags.add(Tag.objects.get_or_create(name=tag)[0])
            self.save()

    def add_like(self, from_profile, is_positive=True):
        rating_delta = Like.objects.add_like(author=from_profile, content_object=self,
                                             is_positive=is_positive)
        if rating_delta:
            self.rating += rating_delta
            self.save()
            self.author.update_reputation(rating_delta)
            return True
        return False

    class Meta:
        ordering = ['-creation_dt']


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    creation_dt = models.DateTimeField(auto_now_add=True)
    is_right = models.BooleanField(default=False)

    def __str__(self):
        return f'#{self.question} by {self.author}'

    def add_like(self, from_profile, is_positive=True):
        rating_delta = Like.objects.add_like(author=from_profile, content_object=self,
                                             is_positive=is_positive)
        if rating_delta:
            self.rating += rating_delta
            self.save()
            self.author.update_reputation(rating_delta)
            return True
        return False

    def set_right(self, from_profile, is_right=True):
        if from_profile != self.author:
            return False
        self.is_right = is_right
        self.save()

    class Meta:
        ordering = ['creation_dt']
