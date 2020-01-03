from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^test/$', views.Test_Base.as_view()),
    url(r'^tests/$', views.testdb.as_view()),
    url(r'^get/$', views.getAll.as_view()),
    url(r'^login/$', views.LoginView.as_view()),

]