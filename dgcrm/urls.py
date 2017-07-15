from django.conf.urls import url

from . import views

app_name = 'dgcrm'
urlpatterns = [
    url(r'^crm/$', views.CrmMain.as_view(), name='crm_main'),
    url(r'^crm/login/$', views.Login.as_view(), name='login'),
    url(r'^crm/logout/$', views.Login.as_view(), name='logout'),
    url(r'^crm/feadback/(?P<feadback_id>[0-9]+)/$', views.DetailedFeadback.as_view(), name='detailed_feadback'),
    url(r'^crm/feadback/feadback_bar/$', views.feadbackBar, name='feadback_bar'),
    url(r'^crm/create_task/$', views.CreateTask.as_view(), name='create_task'),
    url(r'^crm/search_feadback/$', views.searchFeadback, name='search_feadback'),
    url(r'^crm/event/(?P<event_id>[0-9]+)/$', views.DetailedEvent.as_view(), name='detailed_event'),
    url(r'^crm/create_event/$', views.CreateEvent.as_view(), name='create_event'),
    url(r'^crm/transfer_event_calendar/(?P<event_id>[0-9]+)/$', views.TransferEvent.as_view(), name='transfer_event_calendar'),
    url(r'^crm/transfer_event/(?P<event_id>[0-9]+)/$', views.transferEvent, name='transfer_event'),
    url(r'^crm/delete_event/(?P<event_id>[0-9]+)/$', views.DeleteEvent.as_view(), name='delete_event'),
    url(r'^crm/delete_result/(?P<event_id>[0-9]+)/(?P<result_id>[0-9]+)/$', views.DeleteResult.as_view(), name='delete_result'),
    url(r'^crm/client/(?P<client_id>[0-9]+)/$', views.DetailedClient.as_view(), name='detailed_client'),
    url(r'^crm/change_week_calendar/$', views.changeWeekCalendar, name='change_week_calendar'),
    url(r'^crm/time/$', views.timeView, name='time'),
]  