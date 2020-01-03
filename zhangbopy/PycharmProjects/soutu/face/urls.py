from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^recognition/$', views.RecogView.as_view(), name='index'),
    url(r'^get_face/$', views.FaceRecognition.as_view(), name='index'),
]