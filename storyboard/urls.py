from django.conf.urls import include
from django.contrib.auth import views as auth_views
from storyboard import views as storyboard_views

from django.contrib import admin
import django.contrib.auth.urls
from django.urls import include, path,re_path



urlpatterns  =[
    re_path(r'^$', storyboard_views.home, name = 'home'),

    re_path(r'^login$', auth_views.LoginView.as_view(template_name='storyboard/login.html'), name= 'login'),

    # re_path(r'^signform$', storyboard_views.signform, name = 'signform'),
    # re_path(r'^nextpage$', storyboard_views.nextpage, name = 'nextpage'),
    # re_path(r'^nextpage2$', storyboard_views.nextpage2, name = 'nextpage2'),
    # re_path(r'^nextpage3$', storyboard_views.nextpage3, name = 'nextpage3'),
    # re_path(r'^nextpage4$', storyboard_views.nextpage4, name = 'nextpage4'),

    # re_path(r'^imagefeedback$', storyboard_views.imagefeedback, name = 'imagefeedback'),
    # re_path(r'^imagefeedback2$', storyboard_views.imagefeedback2, name = 'imagefeedback2'),
    # re_path(r'^imagefeedback3$', storyboard_views.imagefeedback3, name = 'imagefeedback3'),
    # re_path(r'^imagefeedback4$', storyboard_views.imagefeedback4, name = 'imagefeedback4'),


    re_path(r'^section1$', storyboard_views.section1_questionpage, name = 'section1'),
    # re_path(r'^section2$', storyboard_views.section2, name = 'section2'),
    # re_path(r'^section3$', storyboard_views.section3, name = 'section3'),
    # re_path(r'^section4$', storyboard_views.section4, name = 'section4'),


    re_path(r'^section1_questionpage/(?P<id>\d+)$', storyboard_views.section1_questionpage, name = 'section1_questionpage'),
    # re_path(r'^section2_questionpage/(?P<id>\d+)$', storyboard_views.section2_questionpage, name = 'section2_questionpage'),
    # re_path(r'^section3_questionpage/(?P<id>\d+)$', storyboard_views.section3_questionpage, name = 'section3_questionpage'),
    # re_path(r'^section4_questionpage/(?P<id>\d+)$', storyboard_views.section4_questionpage, name = 'section4_questionpage'),

    re_path(r'^changehint$', storyboard_views.changehint, name="changehint")

    ]
