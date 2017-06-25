from django.conf.urls import url

from . import views

app_name = 'main'
urlpatterns = [
    url(r'^$', views.Main.as_view(), name='main'),
    url(r'^price/$', views.Price.as_view(), name='price'),
    # url(r'^ajax_price/$', views.ajax_price, name='ajax_price'),
    url(r'^more_reviews/$', views.more_reviews, name='more_reviews'),
]  