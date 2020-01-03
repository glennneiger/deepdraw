from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^show/$', views.ShowView.as_view(), name='index'),
    url(r'^guide/$', views.GuideView.as_view()),
    url(r'^get_feature/$', views.Get_Feature.as_view()),
]
