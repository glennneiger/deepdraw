
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.indexView.as_view(), name='index'),
    url(r'^analysis/$',views.analysis_v2_View.as_view()),
    url(r'^index_v2/$', views.index_v2_View.as_view(), name='index'),
]

