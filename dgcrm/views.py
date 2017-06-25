import random
import re
import json
import operator

from itertools import chain
from datetime import datetime, timedelta, timezone, date, time

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.views import View
from django.views.generic.detail import DetailView
from django.conf import settings
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.conf import settings


from .forms import EventForm, ResultForm, SearchForm, FeadbackForm, SearchFeadbackForm
from main.models import ServiceCategory, Service, DetailedService
from .models import Event, Client, Feadback, Result, ClientServiceLinker, CanceledEvent

from django.db.models import F, Q

from .Day import Day


def dayPeriods(hour=9, minute=0, second=0):
    start_day = datetime.time(hour, minute, second)


class EventPeriod(object):
    def __init__(self, event_obj):
        self.event_start = event_obj.data_time
        self.event_end = event_obj.data_time + timedelta(hours=event_obj.duration.hour, minutes=event_obj.duration.minute)

    def __str__(self):
        return "%s %s"%(str(self.event_start), str(self.event_end))

class Period(object):
    def __init__(self, start_period, length_period = timedelta(minutes=30)):
        self.period_datetime = str(start_period)
        self.render = "{0:%H:%M}".format(start_period.time())
        self.start_period = start_period
        self.length_period = length_period
        self.end_period = start_period + length_period
        self.start_event = None
        self.event = None
        # self.contain_event = None
        self.in_past = None

    def __str__(self):
        return "%s %s"%(self.start_period, self.event)

    def isPeriodInPast(self):
        if self.end_period < timezone.now():
            self.in_past = True
            return True
        return False

    def isEventStartInPeriod(self, event_obj=None):
        event_period_obj = EventPeriod(event_obj)
        if event_period_obj == None or event_obj == None:
            return False

        eve_st_gte_per_st = event_period_obj.event_start >= self.start_period
        eve_st_lt_per_en = event_period_obj.event_start < self.end_period
        if eve_st_gte_per_st and eve_st_lt_per_en:
            # Period.extendPeriod(self, event_period_obj)
            # while self.end_period < event_period_obj.event_end:
            #     self.end_period += self.length_period
            self.start_event = True
            return True
        return False

    def isEventEndInPeriod(self, event_obj=None):
        event_period_obj = EventPeriod(event_obj)
        if event_period_obj == None or event_obj == None:
            return False

        eve_en_gt_per_st = event_period_obj.event_end > self.start_period
        eve_en_lte_per_en = event_period_obj.event_end <= self.end_period
        if eve_en_gt_per_st and eve_en_lte_per_en:
            # Period.extendPeriod(self, event_period_obj)
            # while self.end_period < event_period_obj.event_end:
            #     self.end_period += self.length_period
            # self.event = event_obj
            return True
        return False

    def extendPeriod(self, event_obj):
        event_period_obj = EventPeriod(event_obj)
        while self.end_period < event_period_obj.event_end:
                self.end_period += self.length_period

    def isEventInPeriod(self, event_obj=None):
        event_period_obj = EventPeriod(event_obj)
        if event_period_obj == None:
            return False
            # self.contain_event = False
        eve_st_gte_per_st = event_period_obj.event_start >= self.start_period
        eve_st_lt_per_en = event_period_obj.event_start < self.end_period
        eve_st_lt_per_st = event_period_obj.event_start < self.start_period
        eve_en_gt_per_st = event_period_obj.event_end > self.start_period
        eve_en_lte_per_en = event_period_obj.event_end <= self.end_period
        eve_en_gt_per_en = event_period_obj.event_end > self.end_period
        # if (eve_st_gte_per_st and eve_st_lt_per_en) or (eve_en_gte_per_st and eve_en_lt_per_en):
        if (eve_st_gte_per_st and eve_st_lt_per_en) or (eve_st_lt_per_st and eve_en_gt_per_en) or(eve_en_gt_per_en and eve_en_lte_per_en) or (eve_en_gt_per_st and eve_en_lte_per_en):
            # self.contain_event = True
            self.event = event_obj
            return True
        return False

class Day(object):

    def timePeriods(self):
        period = Period(self.start_day)

        period_list = []
        event_list = list(self.event_list)
        stop = 20
        while period.end_period <= self.end_day:# or stop > 0:
            stop -= 1
            # print(period)
            period.isPeriodInPast()
            if len(event_list) > 0:
                event_obj = event_list[0]
                # event_period_obj = EventPeriod(event_obj)
                # print(event_period_obj)
                # print(period.isEventStartInPeriod(event_period_obj, event_obj))
                if period.isEventStartInPeriod(event_obj):
                    period.isEventInPeriod(event_obj)
                    # period.event = event_obj
                    period.extendPeriod(event_obj)
                    event_list.pop(0)

            period_list.append(period)
            period = Period(period_list[-1].end_period)

        return period_list

    def __init__(self, event_list=None, day_date=datetime.date(timezone.now()), start_day=time(9, 0, 0), end_day=time(20, 0, 0)):

        weekdays_name = {1:"Понедельник",
                         2:"Вторник",
                         3:"Среда",
                         4:"Четверг",
                         5:"Пятница",
                         6:"Суббота",
                         7:"Воскресенье"}
        self.event_list = event_list
        self.day_date = day_date
        self.start_day = datetime.combine(self.day_date, start_day)
        self.end_day = datetime.combine(self.day_date, end_day)
        # print(self.start_day, self.end_day)
        self.calendar_data = self.day_date.isocalendar()
        self.day_of_week = weekdays_name[self.day_date.isoweekday()]
        self.time_periods = Day.timePeriods(self)
        self.sorted_time_periods = sorted(self.time_periods, key=lambda x: x.start_period)
        # self.sorted_time_periods = sorted(self.time_periods.items(), key=operator.itemgetter(0))
    
    def __str__(self):
        return "{0:%d} {0:%m} {0:%Y}".format(self.day_date)

    def __iter__(self):
        return iter(self.sorted_time_periods)


class WeekDay(Day):

    def timePeriods(self):
        period = Period(self.start_day)

        period_list = []
        event_list = list(self.event_list)
        stop = 20
        while period.end_period <= self.end_day:# or stop > 0:
            stop -= 1
            # print(period)
            period.isPeriodInPast()
            if len(event_list) > 0:
                event_obj = event_list[0]
                # event_period_obj = EventPeriod(event_obj)
                
                # print(event_period_obj)
                print(period.isEventStartInPeriod(event_obj))
                print(period.isEventEndInPeriod(event_obj))
                # if period.isEventInPeriod(event_obj):
                #     period.contain_event = True
                # if period.isEventStartInPeriod(event_obj):
                #     period.event = event_obj
                period.isEventInPeriod(event_obj)
                period.isEventStartInPeriod(event_obj)
                if period.isEventEndInPeriod(event_obj):
                    event_list.pop(0)

            period_list.append(period)
            period = Period(period_list[-1].end_period)

        return period_list

    def __init__(self, event_list=None, day_date=datetime.date(datetime.now(timezone.utc)), start_day=time(9, 0, 0), end_day=time(20, 0, 0)):
        Day.__init__(self, event_list, day_date, start_day, end_day)

        weekdays_name = {1:"Понедельник",
                         2:"Вторник",
                         3:"Среда",
                         4:"Четверг",
                         5:"Пятница",
                         6:"Суббота",
                         7:"Воскресенье"}

        self.calendar_data = self.day_date.isocalendar()
        self.day_of_week = weekdays_name[self.day_date.isoweekday()]
        self.time_periods = WeekDay.timePeriods(self)
        self.sorted_time_periods = sorted(self.time_periods, key=lambda x: x.start_period)

    

class Week(object):

    def weekDays(self):
        days_list = []
        current_day = self.start_week
        next_day = self.start_week + timedelta(days=1)
        for day in range(7):
            q_start_day = Q(data_time__gte=current_day)
            q_end_day = Q(data_time__lt=next_day)
            day_event_list = self.event_list.filter(q_start_day, q_end_day)
            # print(day_event_list)
            day = WeekDay(day_event_list, current_day)
            # print(day)
            days_list.append(day)
            # print(current_day)
            current_day += timedelta(days=1)
            next_day += timedelta(days=1)

        return days_list

    def __init__(self, event_list=None, date_time=datetime.now(timezone.utc), start_day=time(9, 0, 0), end_day=time(20, 0, 0)):

        self.start_week = datetime.date(date_time-timedelta(days=datetime.weekday(date_time)))
        self.end_week = self.start_week + timedelta(days=7)
        self.event_list = event_list
        self.day_date = datetime.date(datetime.now(timezone.utc))
        self.start_day = datetime.combine(self.day_date, start_day)
        self.end_day = datetime.combine(self.day_date, end_day)
        self.week_days = Week.weekDays(self)

    def __str__(self):
        return iter(self.week_days)

    def __iter__(self):
        return iter(self.week_days)

class Login(View):
    
    def get(self, request):
        login_form = AuthenticationForm()
        return render(request, "login.html", {"login_form": login_form})

    def post(self, request):
        if request.POST.get("submit") == "login":

            login_form = AuthenticationForm(None, data=request.POST)
            # return HttpResponse(login_form)
            if login_form.is_valid():
                # return HttpResponse(123)
                client_data = login_form.cleaned_data
                user = authenticate(request, **login_form.cleaned_data)
                if user is not None:
                    login(request, user)
                    return redirect('/crm/')
                return HttpResponse(user)
            # return HttpResponse("isn't valid")
        elif request.POST.get("submit") == "logout":
            logout(request)

        return redirect('/crm/login/')


class CrmMain(View):


    def byDay(self):
        min_datetime = datetime.date(timezone.now())
        max_datetime = datetime.date(timezone.now())+timedelta(days=1)
        q_object = Q()
        q_object &= Q(data_time__gt=min_datetime)
        q_object &= Q(data_time__lt=max_datetime)
        return q_object

    def byWeek(self):
        min_datetime = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.weekday(datetime.now(timezone.utc))))
        max_datetime = min_datetime+timedelta(days=7)
        q_object = Q()
        q_object &= Q(data_time__gt=min_datetime)
        q_object &= Q(data_time__lt=max_datetime)
        return q_object

    def byMonth(self):
        min_datetime = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.now(timezone.utc).day-1))
        max_datetime = date(int(min_datetime.year), int(min_datetime.month)+1, 1)
        q_object = Q()
        q_object &= Q(data_time__gte=min_datetime)
        q_object &= Q(data_time__lt=max_datetime)
        return q_object

    def eventsOnday(self):
        events = Event.objects.all().filter(CrmMain.byDay(self)).order_by('data_time')
        if events.count() < 1:
            return []
        return events

    def eventsOnweek(self):
        events = Event.objects.all().filter(CrmMain.byWeek(self)).order_by('data_time')
        if events.count() < 1:
            return []
        return events

    def eventsOnmonth(self):
        events = Event.objects.all().filter(CrmMain.byMonth(self)).order_by('data_time')
        if events.count() < 1:
            return []
        return events

    def get(self, request):
        if request.user.is_authenticated:
            context = {"user": request.user}
            serch_form = SearchForm()#initial={'search': '%sпоиск'%search_icon})
            serch_feadback_form = SearchFeadbackForm()
            feadback_list_inwork = Feadback.objects.filter(has_event=False).order_by('id')
            feadback_list_done = Feadback.objects.filter(has_event=True).order_by('-id')
            feadback_list = list(feadback_list_inwork)+list(feadback_list_done)
            event_list = CrmMain.eventsOnday(self)
            periods = Day(event_list=CrmMain.eventsOnday(self))
            week_periods = Week(event_list=CrmMain.eventsOnweek(self))
            client_list = Client.objects.all()
            # return HttpResponse(CrmMain.eventsOnday(self))
            context["serch_form"] = serch_form
            context["serch_feadback_form"] = serch_feadback_form
            context["feadback_list"] = feadback_list
            context["event_list"] = event_list
            context["client_list"] = client_list
            context["periods"] = periods
            context["week_periods"] = week_periods
            context["main_page"] = True
            return render(request, "crm.html", context)
        else:
            # return HttpResponse("CRM not login")
            return redirect('/crm/login/')

    def post(self, request):
        context = {}
        search_feadback = u"%s"%str(request.POST.get("search_feadback"))
        # print(search_feadback)
        serch_all = re.findall(u'[\u0400-\u0500]+', search_feadback, re.U)
        print(serch_all)
       
        if request.is_ajax() and search_feadback:
            to_find_fn_and_ln = re.match(u"(?P<first_name>[\u0400-\u0500]+) (?P<last_name>[\u0400-\u0500]+)", search_feadback, re.U)
            # print(to_find_fn_and_ln)

            to_find_fn_or_ln = re.match(u"^(?P<some_name>[\u0400-\u0500]+)$|^([\u0400-\u0500]+[\s]+)$", search_feadback, re.U)
            # print(to_find_fn_or_ln)

            to_find_tel = re.match(r"^(?:([+]\d{1,2}))?[\s.-]?(\d{3})?[\s.-]?(\d{3})?[\s.-]?(\d{2})?[\s.-]?(\d{2})$", search_feadback, re.U)
            # print(to_find_tel)

            if to_find_fn_and_ln:
                # print(to_find_fn_and_ln.group('first_name'))
                q_first = Q(first=to_find_fn_and_ln.group('first_name'))
                q_last = Q(last=to_find_fn_and_ln.group('last_name'))
                feadback_list = Feadback.objects.filter(q_first, q_last).order_by('id')
            elif to_find_fn_or_ln:
                some_name = re.findall(u'[\u0400-\u0500]+', to_find_fn_or_ln.group(0), re.U)[0]
                print(some_name)
                q_some1 = Q(first__contains=some_name)
                q_some2 = Q(last__contains=some_name)
                    
                feadback_list = Feadback.objects.filter(q_some1 | q_some2).order_by('id')
            elif to_find_tel:
                q_tel = Q(tel=to_find_tel.group())
                feadback_list = Feadback.objects.filter(q_tel).order_by('id')
            else:
                feadback_list = [None]
            context["feadback_list"] = feadback_list
            
        return render(request, "feadback_list_ajax.html", context)


class DetailedFeadback(View):

    def get(self, request, feadback_id):        
        feadback = get_object_or_404(Feadback, pk=feadback_id)
        event_form = EventForm(initial={'feadback': feadback})
        context = {}
        context["feadback"] = feadback
        context["event_form"] = event_form
        return render(request, "detailed_feadback.html", context)

    def post(self, request, feadback_id):
        feadback = get_object_or_404(Feadback, pk=feadback_id)
        client = feadback.client
        event_form = EventForm(request.POST)
        if event_form.is_valid():

            event_data = event_form.cleaned_data
            event_data["client"] = client
            event_update_obj, event_create_bool = Event.objects.update_or_create(feadback=feadback, defaults=event_data)
            feadback.has_event = True
            feadback.save()
            # if event_create_bool:
            #     event_form["feadback"].client.services.add(event_update_obj.detailed_service)
            # else:
            #     event_form["feadback"].client.services.
            return redirect('/crm/')


class DetailedEvent(View):

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        result_form = ResultForm(initial={'event': event,
                                          'service': event.detailed_service, 
                                          'date': (event.data_time + timedelta(hours=event.duration.hour, minutes=event.duration.minute))})
        context = {}
        context["event"] = event
        context["result_form"] = result_form
        return render(request, "detailed_event.html", context)

    def post(self, request, event_id):
        result_form = ResultForm(request.POST, request.FILES)
        event = get_object_or_404(Event, pk=event_id)
        client = get_object_or_404(Event, pk=event_id).feadback.client
        if result_form.is_valid():
            # photo = result_form.cleaned_data["photo"]
            event.successful = result_form.cleaned_data["successful"]
            event.save()
            result_data = result_form.cleaned_data
            result_data["event"] = event
            result_data["client"] = client
            result_data["service"] = event.detailed_service
            del result_data["successful"]
            result_update_obj, result_create_bool = Result.objects.update_or_create(event=event, defaults=result_data)
            
            # return HttpResponse(Event.objects.get(id=event_id).data_time)
            # ClientResultLinker.objects.create(result=result_update_obj, client=client, photo=photo, date=event.data_time)
            ClientServiceLinker.objects.create(service=event.detailed_service, client=client, date=event.data_time)
            # client = get_object_or_404(Client, pk=Event.objects.get(pk=event_id))
            return redirect('/crm/')
        return HttpResponse(result_form)


class DetailedClient(View):

    def get(self, request, client_id):
        client = get_object_or_404(Client, pk=client_id)
        result_list = Result.objects.filter(client=client)
        detailed_service_list = ClientServiceLinker.objects.filter(client=client)
        context = {}
        context["client"] = client
        context["result_list"] = result_list
        context["detailed_service_list"] = detailed_service_list
        return render(request, "detailed_client.html", context)


class CreateEvent(View):

    def get(self, request):        
        # feadback = get_object_or_404(Feadback, pk=feadback_id)
        datetime = request.GET.get("datetime")
        duration = time(1, 0)
        feadback_form = FeadbackForm(initial={})
        event_form = EventForm(initial={'data_time': datetime, 'duration': duration})

        context = {}
        context["feadback_form"] = feadback_form
        context["event_form"] = event_form
        return render(request, "create_event.html", context)

    def post(self, request):
        feadback_form = FeadbackForm(request.POST)
        event_form = EventForm(request.POST)
        if event_form.is_valid() and feadback_form.is_valid():
            feadback_data = feadback_form.cleaned_data
            client_data = feadback_form.cleaned_data.copy()
            del client_data['wish']
            client_obj, created = Client.objects.get_or_create(tel=client_data['tel'], defaults=client_data)
            feadback_data["client"] = client_obj
            feadback_data["has_event"] = True
            event_data = event_form.cleaned_data
            feadback = Feadback.objects.create(**feadback_data)
            event_data["feadback"] = feadback
            q1 = Q(data_time__gte=event_data["data_time"])
            q2 = Q(data_time__lt=(event_data["data_time"] + timedelta(hours=event_data["duration"].hour, minutes=event_data["duration"].minute)))
            if Event.objects.filter( q1 & q2).count() < 1:
                event = Event.objects.create(**event_data)
                return redirect('/crm/')
            # event_update_obj, event_create_bool = Event.objects.update_or_create(feadback=feadback, defaults=event_data)
            # feadback.has_event = True
            # feadback.save()
            # if event_create_bool:
            #     event_form["feadback"].client.services.add(event_update_obj.detailed_service)
            # else:
            #     event_form["feadback"].client.services.
            else:
                return HttpResponse('недостаточно времени')
        return HttpResponse('feadback_form {}  event_form  {}'%(event_form.is_valid(), feadback_form.is_valid()))


class TransferEvent(CrmMain):

    def get(self, request, event_id):
        context = {"event_id": event_id}
        week_periods = Week(event_list=CrmMain.eventsOnweek(self))
        context["week_periods"] = week_periods
        return render(request, "transfer_event_calendar.html", context)

def cancelEvent(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    data = {}
    for f in Event._meta.get_fields():
        if f.name != "id":
            print(f.name)
            data[f.name] = getattr(event, f.name)
    # print(type(data["feadback"]))
    # return HttpResponse(type(data["feadback"]))
    # CanceledEvent.objects.create()
    obj, created = CanceledEvent.objects.update_or_create(defaults=data)
    event.delete()
    # return HttpResponse(obj)
    return redirect('/crm/')


def transferEvent(request, event_id):
    datetime = request.GET.get("datetime")
    event = get_object_or_404(Event, pk=event_id)
    data = {"data_time" : datetime}
    obj, created = Event.objects.update_or_create(pk=event_id, defaults=data)
    return redirect('/crm/')

def searchFeadback(request):
    pass

def feadbackBar(request):

    if request.method== "POST" and request.is_ajax():
        context = {}
        if request.POST.get("filter_type") == "all":
            feadback_list_inwork = Feadback.objects.filter(has_event=False).order_by('id')
            feadback_list_done = Feadback.objects.filter(has_event=True).order_by('-id')
            feadback_list = list(feadback_list_inwork)+list(feadback_list_done)
            context["feadback_list"] = feadback_list
            return render(request, "feadback_list_ajax.html", context)

        elif request.POST.get("filter_type") == "to_work":
            feadback_list = Feadback.objects.filter(has_event=False).order_by('id')
            context["feadback_list"] = feadback_list
            return render(request, "feadback_list_ajax.html", context)

        elif request.POST.get("filter_type") == "processed":
            feadback_list = Feadback.objects.filter(has_event=True).order_by('-id')
            context["feadback_list"] = feadback_list
            return render(request, "feadback_list_ajax.html", context)



def timeView(request):
    min_datetime = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.weekday(datetime.now(timezone.utc))))
    max_datetime = min_datetime+timedelta(days=7)
    
    # return HttpResponse(max_d)
    return HttpResponse(datetime.combine(min_datetime, datetime.min.time()))