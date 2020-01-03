from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^sign/$', views.SignupView.as_view(), name='index'),
    url(r'^user/login/$', views.LoginView.as_view()),
    url(r'^tourist/$', views.TouristView.as_view()),
    url(r'^put_task/$', views.PutTaskView.as_view()),
    url(r'^start_task/$', views.StartTaskView.as_view()),
    url(r'^get_history/$',views.GetHistoryPicView.as_view()),
    url(r'^pic/$', views.PicView.as_view()),
    url(r'^get_pic/$',views.GetPicView.as_view()),
    url(r'^msg/$', views.MsgView.as_view()),
    url(r'^get_oss_key/$', views.OssKeyView.as_view()),
    url(r'^download/$', views.Download.as_view(), name='download'),
]
