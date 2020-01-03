from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.indexView.as_view(), name='index'),
    url(r'^analysis/$',views.analysisView.as_view(), name='index')
]
