from django.conf.urls import url

from . import views
urlpatterns = [
    url(r'^show/$', views.ShowView.as_view(), name='index'),
    ]