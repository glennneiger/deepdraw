from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', views.LoginView.as_view()),
    url(r'^get_task/$', views.GetTask.as_view()),
    url(r'^read_csv/$', views.Read_csv.as_view()),
    url(r'^submit_task/$', views.Submit_Task.as_view()),
]
