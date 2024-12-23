"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls import include
import storyboard.urls
from storyboard import views as storyboard_views
from django.contrib.auth import views as auth_views

import django.contrib.auth.urls
from django.urls import include, path, re_path


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^storyboard/', include(storyboard.urls)),
    re_path(r'^$', storyboard_views.home),

    re_path(r'^login$', auth_views.LoginView.as_view(template_name='storyboard/login.html'), name= 'login'),
]
