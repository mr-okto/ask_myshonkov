from django.contrib import admin

# Register your models here.

from .models import Question, Answer, Profile, Like, Tag
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Profile)
admin.site.register(Like)
admin.site.register(Tag)
