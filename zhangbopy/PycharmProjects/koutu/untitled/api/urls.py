from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$',views.zjd_testView.as_view()),
    url(r'^index/$', views.IndexView.as_view(), name='index'),
    url(r'^bar/$', views.ChartView.as_view(), name='bar'),
    url(r'^echarts/$', views.VisualView.as_view(), name='echarts'),
    url(r'^user/login/$', views.LoginView.as_view()),
    url(r'^user/signup/$', views.SignupView.as_view()),
    url(r'^oss/$', views.Oss.as_view()),
    url(r'^tourist/$', views.TouristView.as_view()),
    url(r'^task/$', views.TaskView.as_view()),
    url(r'^put_task/$', views.PutTaskView.as_view()),
    url(r'^start_task/$', views.StartTaskView.as_view()),
    url(r'^get_task/$',views.GetTaskView.as_view()),
    url(r'^get_history/$',views.GetHistoryPicView.as_view()),
    url(r'^pic/$', views.PicView.as_view()),
    url(r'^get_pic/$',views.GetPicView.as_view()),
    url(r'^msg/$', views.MsgView.as_view()),
    url(r'^get_oss_key/$', views.OssKeyView.as_view()),
    url(r'^mtp_upload/$', views.mtploadView.as_view()),
    url(r'^phone_log/$', views.phonelogView.as_view()),
    url(r'^mtp_upload_v2/$', views.testView.as_view()),
    url(r'^index_v2/$', views.Index_v2_View.as_view(), name='index'),
    url(r'^download/$', views.Download.as_view(), name='download'),
]
