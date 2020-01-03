from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^write/$', views.Read_csv.as_view()),
    url(r'^count/$', views.Count.as_view()),
]