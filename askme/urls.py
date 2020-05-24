"""askme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('', views.index,  name='index'),
    path('hot/', views.hot_questions, name='hot'),
    path('tag/<slug:tag_name>/', views.tagged_questions, name='tagged'),
    path('ask/', views.ask,  name='ask'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('register/', views.register, name='register'),
    path('question/<int:qid>/', views.view_question, name='question'),
    path('settings/', views.profile_settings, name='settings'),
    path('ajax/like/', views.ajax_like, name='ajax_like'),
    path('ajax/mark_correct/', views.ajax_mark_correct, name='ajax_mark_correct'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
