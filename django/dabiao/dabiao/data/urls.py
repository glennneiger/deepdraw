from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^test/$', views.Test_Base.as_view()),
    url(r'^tests/$', views.testdb.as_view()),
    url(r'^get/$', views.getAll.as_view()),
    url(r'^login/$', views.LoginView.as_view()),
    url(r'^index/$', views.IndexView.as_view()),
    url(r'^getTask/$', views.GetTask.as_view()),
    url(r'^submit/$', views.Submit.as_view()),
    url(r'^check/$', views.CheckLogin.as_view()),
    url(r'^count/$', views.Count.as_view()),
    url(r'^write/$', views.Read_csv.as_view()),
]
