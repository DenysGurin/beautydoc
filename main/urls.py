from django.conf.urls import url

from . import views

app_name = 'main'
urlpatterns = [
    url(r'^$', views.Main.as_view(), name='main'),
    url(r'^price/(?P<category>[0-9]+)/(?P<service>[0-9]+|)$', views.Price.as_view(), name='price'),
    url(r'^more_reviews/$', views.more_reviews, name='more_reviews'),
]  