from django.conf.urls import url
from . import views

urlpatterns = [
 #   url(r'^login/$', views.csv_2_db.as_view()),
    url(r'^authentiction/$', views.AuthentictionView.as_view()),
    url(r'^index/$', views.IndexView.as_view()),
    url(r'^agg/$', views.AggView.as_view()),
    url(r'^date/$', views.DateView.as_view()),
    url(r'^oldday/$', views.OlddayView.as_view()),
    url(r'^merchant_date/$', views.merchantView.as_view()),
    url(r'^merchant_agg/$', views.merchant_aggView.as_view()),
    url(r'^get_all/$', views.GetAll.as_view()),
    url(r'^get_all_data/$', views.GetAllData.as_view()),
    url(r'^show/$', views.ShowView.as_view()),
    url(r'^test/$', views.ShowViewTest.as_view()),
]
