from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^show/$', views.ShowView.as_view(), name='index'),
    url(r'^guide/$', views.GuideView.as_view()),
    url(r'^get_feature/$', views.Get_Feature.as_view()),
    url(r'^get_urls/$', views.Get_Urls.as_view()),
    url(r'^get_box/$', views.Get_Box.as_view()),
    url(r'^test/$',views.test),
    url(r'^test2/$', views.test2),
    url(r'^home/$', views.test3),
    url(r'^tests/$', views.FeatureAndWord.as_view()),
    url(r'^vue/$', views.ShowVue.as_view()),

]