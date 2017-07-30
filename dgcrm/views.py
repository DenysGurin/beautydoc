import random
import re
import json
import operator

from itertools import chain
from datetime import datetime, timedelta, date, time
import calendar
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.views import View
from django.views.generic.detail import DetailView
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.conf import settings


from .forms import *
from main.models import ServiceCategory, Service, DetailedService
from .models import *

from django.db.models import F, Q

from .Day import Day


def dayPeriods(hour=9, minute=0, second=0):

    start_day = datetime.time(hour, minute, second)


class Search(object):

    def __init__(self, search_str):
        # super(Search, self).__init__(search_feadback)
        self.to_find_fn_and_ln = re.match(u"(?P<first_name>[\u0400-\u0500]+) (?P<last_name>[\u0400-\u0500]+)",
                                          search_str, re.U)
        self.to_find_fn_or_ln = re.match(u"^(?P<some_name>[\u0400-\u0500]+)$|^([\u0400-\u0500]+[\s]+)$",
                                         search_str, re.U)
        self.to_find_tel = re.match(r"^(?:([+]\d{1,2}))?[\s.-]?(\d{3})?[\s.-]?(\d{3})?[\s.-]?(\d{2})?[\s.-]?(\d{2})$",
                                    search_str, re.U)
        self.to_find_email = re.match(r'(?:[a-z0-9!#$%&*+/=?^_`{|}~-]+'
                                      r'(?:\.[a-z0-9!#$%&*+/=?^_`{|}~-]+)*|'
                                      r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|'
                                      r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+'
                                      r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                                      r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:'
                                      r'(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|'
                                      r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])', search_str, re.U)


    def serchFeadback(self):
        if self.to_find_fn_and_ln:
            # print(to_find_fn_and_ln.group('first_name'))
            q_first = Q(first=self.to_find_fn_and_ln.group('first_name'))
            q_last = Q(last=self.to_find_fn_and_ln.group('last_name'))
            feadback_list = Feadback.objects.filter(q_first, q_last).order_by('id')
        elif self.to_find_fn_or_ln:
            some_name = re.findall(u'[\u0400-\u0500]+', self.to_find_fn_or_ln.group(0), re.U)[0]
            # print(some_name)
            q_some1 = Q(first__contains=some_name)
            q_some2 = Q(last__contains=some_name)

            feadback_list = Feadback.objects.filter(q_some1 | q_some2).order_by('id')
        elif self.to_find_tel:
            q_tel = Q(tel=self.to_find_tel.group())
            feadback_list = Feadback.objects.filter(q_tel).order_by('id')
        else:
            feadback_list = [None]

        return feadback_list


    def serchClient(self):
        if self.to_find_fn_and_ln:
            # print(to_find_fn_and_ln.group('first_name'))
            q_first = Q(first=self.to_find_fn_and_ln.group('first_name'))
            q_last = Q(last=self.to_find_fn_and_ln.group('last_name'))
            client_list = Client.objects.filter(q_first, q_last).order_by('id')
        elif self.to_find_fn_or_ln:
            some_name = re.findall(u'[\u0400-\u0500]+', self.to_find_fn_or_ln.group(0), re.U)[0]
            # print(some_name)
            q_some1 = Q(first__contains=some_name)
            q_some2 = Q(last__contains=some_name)

            client_list = Client.objects.filter(q_some1 | q_some2).order_by('id')
        elif self.to_find_tel:
            q_tel = Q(tel=self.to_find_tel.group())
            client_list = Client.objects.filter(q_tel).order_by('id')
        elif self.to_find_email:
            q_email = Q(email=self.to_find_tel.group())
            client_list = Client.objects.filter(q_email).order_by('id')
        else:
            client_list = [None]

        return client_list


def searchByNameTel(search_feadback):


    to_find_fn_and_ln = re.match(u"(?P<first_name>[\u0400-\u0500]+) (?P<last_name>[\u0400-\u0500]+)", search_feadback,
                                 re.U)
    # print(to_find_fn_and_ln)

    to_find_fn_or_ln = re.match(u"^(?P<some_name>[\u0400-\u0500]+)$|^([\u0400-\u0500]+[\s]+)$", search_feadback, re.U)
    # print(to_find_fn_or_ln)

    to_find_tel = re.match(r"^(?:([+]\d{1,2}))?[\s.-]?(\d{3})?[\s.-]?(\d{3})?[\s.-]?(\d{2})?[\s.-]?(\d{2})$",
                           search_feadback, re.U)
    # print(to_find_tel)

    if to_find_fn_and_ln:
        # print(to_find_fn_and_ln.group('first_name'))
        q_first = Q(first=to_find_fn_and_ln.group('first_name'))
        q_last = Q(last=to_find_fn_and_ln.group('last_name'))
        feadback_list = Feadback.objects.filter(q_first, q_last).order_by('id')
    elif to_find_fn_or_ln:
        some_name = re.findall(u'[\u0400-\u0500]+', to_find_fn_or_ln.group(0), re.U)[0]
        # print(some_name)
        q_some1 = Q(first__contains=some_name)
        q_some2 = Q(last__contains=some_name)

        feadback_list = Feadback.objects.filter(q_some1 | q_some2).order_by('id')
    elif to_find_tel:
        q_tel = Q(tel=to_find_tel.group())
        feadback_list = Feadback.objects.filter(q_tel).order_by('id')
    else:
        feadback_list = [None]

    return feadback_list

class QueryByPeriod(object):


    @classmethod
    def byDay(cls, min_datetime=None):
        if min_datetime:
            min_date = min_datetime.date()
        else:
            min_date = datetime.date(timezone.now())
        max_date = min_date + timedelta(days=1)
        q_object = Q()
        q_object &= Q(date__gte=min_date)
        q_object &= Q(date__lt=max_date)
        return q_object

    @classmethod
    def byWeek(cls, min_datetime=None):
        if min_datetime:
            min_date = datetime.date(min_datetime - timedelta(days=datetime.weekday(min_datetime)))
        else:
            min_date = datetime.date(
                datetime.now(timezone.utc) - timedelta(days=datetime.weekday(datetime.now(timezone.utc))))

        max_date = min_date+timedelta(days=7)
        q_object = Q()
        q_object &= Q(date__gt=min_date)
        q_object &= Q(date__lt=max_date)
        return q_object

    @classmethod
    def byMonth(cls, min_datetime=None):
        if min_datetime:
            min_date = datetime.date(min_datetime - timedelta(days=min_datetime.day - 1))
        else:
            min_date = datetime.date(datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).day - 1))

        max_date = date(int(min_date.year), int(min_date.month)+1, 1)
        q_object = Q()
        q_object &= Q(date__gte=min_date)
        q_object &= Q(date__lt=max_date)
        return q_object

    @staticmethod
    def queryOnday(query_obj, min_datetime = None):
        print(query_obj)
        query = query_obj.filter(QueryByPeriod.byDay(min_datetime))
        print(query)
        if query.count() < 1:
            return None
        return query.order_by('date')

    @staticmethod
    def queryOnweek(query_obj, min_datetime = None):
        query = query_obj.filter(QueryByPeriod.byWeek(min_datetime))
        if query.count() < 1:
            return None
        return query.order_by('date')

    @staticmethod
    def queryOnmonth(query_obj, min_datetime = None):
        query = query_obj.filter(QueryByPeriod.byMonth(min_datetime))
        if query.count() < 1:
            return None
        return query.order_by('date')


class EventList(object):


    @classmethod
    def byDay(cls, min_datetime):
        if not min_datetime:
            min_datetime = datetime.date(timezone.now())
        else:
            min_datetime = min_datetime.date()
        max_datetime = min_datetime + timedelta(days=1)
        q_object = Q()
        q_object &= ~Q(status="failed")
        q_object &= Q(date_time__gt=min_datetime)
        q_object &= Q(date_time__lt=max_datetime)
        return q_object

    @classmethod
    def byWeek(cls, min_datetime):
        if not min_datetime:
            min_datetime = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.weekday(datetime.now(timezone.utc))))
        else:
            min_datetime = datetime.date(min_datetime-timedelta(days=datetime.weekday(min_datetime)))
        max_datetime = min_datetime+timedelta(days=7)
        q_object = Q()
        q_object &= ~Q(status="failed")
        q_object &= Q(date_time__gt=min_datetime)
        q_object &= Q(date_time__lt=max_datetime)
        return q_object

    @classmethod
    def byMonth(cls, min_datetime):
        if not min_datetime:
            min_datetime = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.now(timezone.utc).day-1))
        else:
           min_datetime = datetime.date(min_datetime-timedelta(days=min_datetime.day-1))
        
        max_datetime = date(int(min_datetime.year), int(min_datetime.month)+1, 1)
        q_object = Q()
        q_object &= ~Q(status="failed")
        q_object &= Q(date_time__gte=min_datetime)
        q_object &= Q(date_time__lt=max_datetime)
        return q_object

    @staticmethod
    def eventsOnday(min_datetime = None):
        events = Event.objects.all().filter(EventList.byDay(min_datetime))
        if events.count() < 1:
            return None
        return events.order_by('date_time')

    @staticmethod
    def eventsOnweek(min_datetime = None):
        events = Event.objects.all().filter(EventList.byWeek(min_datetime))
        if events.count() < 1:
            return None
        return events.order_by('date_time')

    @staticmethod
    def eventsOnmonth(min_datetime = None):
        events = Event.objects.all().filter(EventList.byMonth(min_datetime))
        if events.count() < 1:
            return None
        return events.order_by('date_time')


class EventPeriod(object):


    def isInPast(self):
        if self.event_start < timezone.now():
            return True
        return False

    def __init__(self, event_obj):
        self.event_start = event_obj.date_time
        self.event_end = event_obj.date_time + timedelta(hours=event_obj.duration.hour, minutes=event_obj.duration.minute)
        self.is_in_past = EventPeriod.isInPast(self)

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
        if self.start_period < timezone.now():
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
        if (eve_st_gte_per_st and eve_st_lt_per_en) or \
                (eve_st_lt_per_st and eve_en_gt_per_en) or \
                (eve_en_gt_per_en and eve_en_lte_per_en) or \
                (eve_en_gt_per_st and eve_en_lte_per_en):
            # self.contain_event = True
            self.event = event_obj
            return True
        return False


class Day(object):


    def timePeriods(self):
        period = Period(self.start_day)
        period_list = []
        if self.event_list:
            event_list = list(self.event_list)
        else:
            event_list = []
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

    def __repr__(self):
        return "{0:%d} {0:%m} {0:%Y}".format(self.day_date)

    def __iter__(self):
        return iter(self.sorted_time_periods)


class WeekDay(Day):

    def timePeriods(self):
        period = Period(self.start_day)

        period_list = []
        if self.event_list:
            event_list = list(self.event_list)
        else:
            event_list = []
        stop = 20
        while period.end_period <= self.end_day:# or stop > 0:
            stop -= 1
            # print(period)
            period.isPeriodInPast()
            if len(event_list) > 0:
                event_obj = event_list[0]
                # event_period_obj = EventPeriod(event_obj)
                
                # print(event_period_obj)
                # print(period.isEventStartInPeriod(event_obj))
                # print(period.isEventEndInPeriod(event_obj))
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

    def __str__(self):
        return "{0:%d} {0:%m} {0:%Y}".format(self.day_date)

    def __iter__(self):
        return iter(self.sorted_time_periods)


class Week(object):

    def weekDays(self):
        days_list = []
        current_day = self.start_week
        next_day = self.start_week + timedelta(days=1)
        for day in range(7):
            q_start_day = Q(date_time__gte=current_day)
            q_end_day = Q(date_time__lt=next_day)
            day_event_list = self.event_list
            if self.event_list:
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
        self.start_date = str(self.start_week)

    def __str__(self):
        return str(self.week_days)

    def __iter__(self):
        return iter(self.week_days)


class Login(View):
    
    def get(self, request):
        login_form = MyAuthenticationForm()
        return render(request, "login.html", {"login_form": login_form})

    def post(self, request):
        if request.POST.get("submit") == "login":

            login_form = MyAuthenticationForm(None, data=request.POST)
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


class LoginRequiredView(LoginRequiredMixin, View):


    login_url = '/crm/login/'
    redirect_field_name = '/crm/login/'


class CrmMain(LoginRequiredView):


    # @classmethod
    # def addClientToEvent(self):
    #     clients = Client.objects.all()
    #     events = Event.objects.all()
    #     for event in events:
    #         if not event.client:
    #             tel = event.feadback.tel
    #             for client in clients:
    #                 if client.tel == tel:
    #                     event.client = client
    #                     event.save()


    def get(self, request):

        # CrmMain.addClientToEvent(self)
        context = {"user": request.user}
        serch_form = SearchForm()#initial={'search': '%sпоиск'%search_icon})
        serch_feadback_form = SearchFeadbackForm()
        feadback_list = Feadback.objects.all()
        feadback_list_inwork = feadback_list.filter(has_event=False)

        if feadback_list_inwork:
            feadback_list_inwork.order_by('date')
        feadback_list_done = feadback_list.filter(has_event=True)

        if feadback_list_done:
            feadback_list_done.order_by('-date')

        feadback_list = list(feadback_list_inwork)+list(feadback_list_done)

        # print(Task.objects.filter(done=False))

        task_list = Task.objects.all().order_by("-date")
        context["task_list"] = task_list

        periods = Day(event_list=EventList.eventsOnday())

        # return HttpResponse(EventList.eventsOnday(self))
        context["serch_form"] = serch_form
        context["serch_feadback_form"] = serch_feadback_form
        context["feadback_list"] = feadback_list

        context["periods"] = periods
        return render(request, "crm_main.html", context)


    def post(self, request):
        context = {}
        search_feadback = u"%s"%str(request.POST.get("search_feadback"))
        # print(search_feadback)
        serch_all = re.findall(u'[\u0400-\u0500]+', search_feadback, re.U)
        # print(serch_all)
       
        if request.is_ajax() and search_feadback:
            print(Search(search_feadback).serchFeadback())
            context["feadback_list"] = Search(search_feadback).serchFeadback()
            # context["feadback_list"] = searchByNameTel(search_feadback)
        return render(request, "crm_main/feadback_list_ajax.html", context)


class CrmCalendar(LoginRequiredView):


    def get(self, request):

        context = {"user": request.user}

        periods = Day(event_list=EventList.eventsOnday())
        week_periods = Week(event_list=EventList.eventsOnweek())

        # return HttpResponse(EventList.eventsOnday(self))

        context["periods"] = periods
        context["week_periods"] = week_periods
        return render(request, "crm_calendar.html", context)

    def post(self, request):
        pass


class CrmClients(LoginRequiredView):


    def get(self, request):

        context = {}
        serch_client_form = SearchClientForm()

        client_list = Client.objects.all()

        context["serch_client_form"] = serch_client_form
        context["client_list"] = client_list

        return render(request, "crm_clients.html", context)

    def post(self, request):
        context = {}
        search_client = u"%s" % str(request.POST.get("search_client"))
        # print(search_client)
        serch_all = re.findall(u'[\u0400-\u0500]+', search_client, re.U)
        # print(serch_all)

        if request.is_ajax() and search_client:
            # print(Search(search_feadback).serchFeadback())
            context["client_list"] = Search(search_client).serchClient()
            # context["feadback_list"] = searchByNameTel(search_feadback)

        return render(request, "crm_clients/clients_list_ajax.html", context)


class QByPeriod(object):


    @classmethod
    def DaysInMonths(cls, from_year_month, to_year_month):
        ### from_year_month == (year, month)
        ### to_year_month == (year, month)

        days_sum = 0
        if from_year_month[0] < to_year_month[0] or \
                (from_year_month[0] == to_year_month[0] and from_year_month[1] < to_year_month[1]):
            for year in range(from_year_month[0], to_year_month[0]+1):
                print(year)
                if year == to_year_month[0]:
                    print(range(from_year_month[1], to_year_month[1]+1))
                    for month in range(from_year_month[1], to_year_month[1]+1):
                        print(month)
                        days_sum += calendar.monthrange(year, month)[1]
                else:
                    print(range(from_year_month[1], 13))
                    for month in range(from_year_month[1], 13):
                        days_sum += calendar.monthrange(year, month)[1]
                    from_year_month[1] = 1
            print(days_sum)
            return days_sum
        else:
            raise "from_month has to be less than to_month"


    @classmethod
    def byMonth(cls, field_name, min_datetime=None):


        current = datetime.now(timezone.utc)

        if min_datetime:
            min_date = datetime.date(min_datetime - timedelta(days=min_datetime.day - 1))
        else:
            min_date = datetime.date(current - timedelta(days=current.day - 1))

        max_date = date(int(min_date.year), int(min_date.month) + 1, 1)
        print(min_date, max_date)
        filter__gte = field_name + '__' + 'gte'
        filter__lt = field_name + '__' + 'lt'

        q_object = Q()
        q_object &= Q(**{filter__gte: min_date})
        q_object &= Q(**{filter__lt: max_date})

        return q_object


    @classmethod
    def byThreeMonths(cls, field_name, min_datetime=None):
        current = datetime.now(timezone.utc)
        to_month = (current.year, current.month-1)

        if (current.month - 2) > 0:
            from_month = (current.year, current.month - 2)
        else:
            from_month = (current.year-1, 12 - (current.month - 2))

        days = QByPeriod.DaysInMonths(from_month,to_month)

        if min_datetime:
            min_date = datetime.date(min_datetime - timedelta(days=min_datetime.day - 1 + days))
        else:
            min_date = datetime.date(
                current - timedelta(days=current.day - 1 + days))

        max_date = date(int(min_date.year), int(min_date.month) + 3, 1)

        filter__gte = field_name + '__' + 'gte'
        filter__lt = field_name + '__' + 'lt'

        q_object = Q()
        q_object &= Q(**{filter__gte: min_date})
        q_object &= Q(**{filter__lt: max_date})

        return q_object


    @classmethod
    def byTwelveMonths(cls, field_name, min_datetime=None):
        current = datetime.now(timezone.utc)
        to_month = [current.year, current.month - 1]

        if (current.month - 12) > 0:
            from_month = [current.year, current.month - 12]
        else:
            from_month = [current.year - 1, 12 + (current.month - 12)]

        print(from_month, to_month)
        days = QByPeriod.DaysInMonths(from_month, to_month)

        if min_datetime:
            min_date = datetime.date(min_datetime - timedelta(days=min_datetime.day - 1 + days))
        else:
            min_date = datetime.date(
                current - timedelta(days=current.day - 1 + days))

        max_date = min_date + timedelta(days=days+calendar.monthrange(current.year, current.month)[1])

        filter__gte = field_name + '__' + 'gte'
        filter__lt = field_name + '__' + 'lt'

        q_object = Q()
        q_object &= Q(**{filter__gte: min_date})
        q_object &= Q(**{filter__lt: max_date})

        return q_object


class QuerySetByPeriod(QByPeriod):


    def __init__(self, Query_set, field_name, min_datetime=None):
        self.Query_set = Query_set
        self.field_name = field_name
        self.min_datetime = min_datetime



    def getByMounth(self):
        return self.Query_set.filter(self.byMonth(self.field_name, self.min_datetime))


    def getThreeMonths(self):
        return self.Query_set.filter(self.byThreeMonths(self.field_name, self.min_datetime))


    def getByTwelveMonths(self):
        return self.Query_set.filter(self.byTwelveMonths(self.field_name, self.min_datetime))

    def __str__(self):
        return str(self.Query_set)


class DataSets(object):

    @staticmethod
    def RatingByEventFrequency(query_set):
        from operator import itemgetter

        services_raiting = {}
        services_list = []
        for event in query_set:
            if event.detailed_service in services_list:
                services_raiting[event.detailed_service] += 1
            else:
                services_list.append(event.detailed_service)
                services_raiting[event.detailed_service] = 0

        return sorted(services_raiting.items(), key=itemgetter(1), reverse=True)

    @staticmethod
    def RatingByDaysLoad(query_set):

        services_raiting = {}
        for day in range(1,8):
            services_raiting[day] = []

        for event in query_set:
            day = event.date_time.isoweekday()
            services_raiting[day].append(event.detailed_service)

        return sorted(services_raiting.items(), key=lambda item: len(item[1]), reverse=True)


class CrmStatistic(LoginRequiredView):


    def get(self, request):

        context = {}
        clients = QuerySetByPeriod(Client.objects.all(), "registration")
        print(clients)

        events = QuerySetByPeriod(Event.objects.all(), "date_time")
        print(clients)

        new_clients_by_month = clients.getByMounth()
        context["new_clients_by_month"] = new_clients_by_month
        print(new_clients_by_month)

        new_clients_by_three_month = clients.getThreeMonths()
        context["new_clients_by_three_month"] = new_clients_by_three_month
        print(new_clients_by_three_month)

        new_clients_by_twelve_month = clients.getByTwelveMonths()
        context["new_clients_by_twelve_month"] = new_clients_by_twelve_month
        print(new_clients_by_twelve_month)

        new_events_by_month = events.getByMounth()
        context["new_events_by_month"] = new_events_by_month
        print("#################")
        print(new_events_by_month)

        new_events_by_three_month = events.getThreeMonths()
        context["new_events_by_three_month"] = new_events_by_three_month
        print(new_events_by_three_month)

        new_events_by_twelve_month = events.getByTwelveMonths()
        context["new_events_by_twelve_month"] = new_events_by_twelve_month
        print(new_events_by_twelve_month)


        raiting_by_event_frequency_sorted = DataSets.RatingByEventFrequency(new_events_by_month)
        context["raiting_by_event_frequency_sorted"] = raiting_by_event_frequency_sorted
        print(raiting_by_event_frequency_sorted)

        raiting_by_days_load_sorted = DataSets.RatingByDaysLoad(new_events_by_month)
        context["raiting_by_days_load_sorted"] = raiting_by_days_load_sorted
        print(raiting_by_days_load_sorted)

        return render(request, "crm_statistic.html", context)


class CrmFinance(LoginRequiredView):

    pass


class DetailedFeadback(LoginRequiredView):


    @classmethod
    def getModelInstanceData(cls, instance):
        data = {}
        for f in instance._meta.get_fields():
            if not f.auto_created:
                data[f.name] = getattr(instance, f.name)
                # print(type(f))
        return data

    def get(self, request, feadback_id):        
        feadback = get_object_or_404(Feadback, pk=feadback_id)
        event_form = EventForm(initial={'feadback': feadback})
        context = {}
        context["feadback"] = feadback
        context["event_form"] = event_form
        return render(request, "detailed_feadback.html", context)

    def post(self, request, feadback_id):
        feadback = get_object_or_404(Feadback, pk=feadback_id)
        # print(DetailedFeadback.getModelInstanceData(self, feadback))
        client_data = DetailedFeadback.getModelInstanceData(feadback)
        del client_data['wish']
        del client_data['date']
        del client_data['has_event']

        client_obj, created = Client.objects.get_or_create(tel=feadback.tel, defaults=client_data)
        event_form = EventForm(request.POST)
        if event_form.is_valid():

            event_data = event_form.cleaned_data
            event_data["client"] = client_obj
            event_update_obj, event_create_bool = Event.objects.update_or_create(feadback=feadback, defaults=event_data)
            feadback.has_event = True
            feadback.save()
            # if event_create_bool:
            #     event_form["feadback"].client.services.add(event_update_obj.detailed_service)
            # else:
            #     event_form["feadback"].client.services.
            return redirect('/crm/')


class ClientCard(LoginRequiredView):


    @classmethod
    def updateModelInstanceData(cls, model_inst, data_dict):
        for key in data_dict.keys():
            setattr(model_inst, key, data_dict[key])
            model_inst.save()

    @classmethod
    def getPrice(cls, event_obj):
        try:
            return getattr(event_obj, "price")
        except AttributeError:
            return None

    def get(self, request, event_id=None, client_id=None):

        print(event_id, client_id)
        context = {}

        if event_id and not client_id:

            print("event")
            event = get_object_or_404(Event, pk=event_id)
            event_period = EventPeriod(event)
            client = event.client
            event_list = Event.objects.filter(client=client).order_by("-date_time")
            event_price = self.getPrice(event)
            print(event_price)

            client_form = ClientForm(initial=client.__dict__)
            price_form = PriceForm(initial=event_price.__dict__)
            result_form = ResultForm(initial={
                'date': (event.date_time + timedelta(hours=event.duration.hour, minutes=event.duration.minute))})
            pay_form = PayForm(initial={
                'date_time': (event.date_time + timedelta(hours=event.duration.hour, minutes=event.duration.minute))})
            detailed_event_form = DetailedEventForm(initial={})

            context["event_id"] = int(event_id)
            context["event"] = event
            context["event_period"] = event_period
        elif client_id and not event_id:
            print("client")
            client = get_object_or_404(Client, pk=client_id)
            event_list = Event.objects.filter(client=client).order_by("-date_time")

            client_form = ClientForm(initial=client.__dict__)
            price_form = PriceForm(initial={})
            result_form = ResultForm(initial={'date': timezone.now()})
            pay_form = PayForm(initial={'date_time': timezone.now()})
            detailed_event_form = DetailedEventForm(initial={})

        context["client"] = client
        context["event_list"] = event_list

        context["client_form"] = client_form
        context["price_form"] = price_form
        context["result_form"] = result_form
        context["pay_form"] = pay_form
        context["detailed_event_form"] = detailed_event_form

        if event_id and not client_id:
            return render(request, "detailed_event.html", context)

        elif client_id and not event_id:
            return render(request, "detailed_client.html", context)


    def post(self, request, event_id=None, client_id=None):

        result_form = ResultForm(request.POST, request.FILES)
        pay_form = PayForm(request.POST)
        detailed_event_form = DetailedEventForm(request.POST)
        client_form = ClientForm(request.POST)
        price_form = PriceForm(request.POST)

        event = get_object_or_404(Event, pk=request.POST.get("event_id"))

        if result_form.is_valid() and request.POST.get("submit") == "add_result":
            result_data = result_form.cleaned_data

            result_data["client"] = event.client
            result_data["detailed_service"] = event.detailed_service

            result = Result.objects.create(**result_data)
            event.results.add(result)
            # return render(request, "create_event.html", {})

        if pay_form.is_valid() and request.POST.get("submit") == "add_pay":
            pay_data = pay_form.cleaned_data
            pay_data["client"] = event.client
            pay_data["detailed_service"] = event.detailed_service
            # pay_update_obj, pay_create_bool = Pay.objects.update_or_create(event=event, defaults=pay_data)
            pay = Pay.objects.create(**pay_data)
            event.pays.add(pay)
            # return render(request, "create_event.html", {})

        if client_form.is_valid() and request.POST.get("submit") == "edit_client":
            client_data = client_form.cleaned_data
            # print(client_data)
            self.updateModelInstanceData(event.client, client_data)
            # event.status = detailed_event_form.cleaned_data["status"]
            event.save()
        print(price_form.is_valid())
        if price_form.is_valid() and request.POST.get("submit") == "edit_price":
            price_data = price_form.cleaned_data
            # print(price_data)
            self.updateModelInstanceData(event.price, price_data)
            # event.status = detailed_event_form.cleaned_data["status"]
            event.save()

        if detailed_event_form.is_valid() and request.POST.get("submit") == None:
            detailed_event_data = detailed_event_form.cleaned_data
            event.status = detailed_event_form.cleaned_data["status"]
            # print(detailed_event_form.cleaned_data["status"])
            event.save()

            # return render(request, "create_event.html", {})

        return redirect("/crm/event/%s" % event_id)


class CreateTask(LoginRequiredView):


    def get(self, request):        

        task_form = TaskForm()#initial={'date_time': datetime, 'duration': duration})

        context = {}
        context["task_form"] = task_form
        return render(request, "create_task.html", context)

    def post(self, request):
        task_form = TaskForm(request.POST)

        if task_form.is_valid():
            task_data = task_form.cleaned_data
            Task.objects.create(**task_data)
            return redirect("/crm")

        return HttpResponse(task_form.is_valid())


class TaskActions(LoginRequiredView):

    def post(self, request):
        if request.method == "POST" and request.is_ajax():
            context = {}
            task_id = request.POST.get("task_id")
            action_flag = request.POST.get("action_flag")
            print(action_flag)
            if action_flag == "done":
                event = get_object_or_404(Task, pk=task_id)
                event.done = True
                event.save()
                context["task_list"] = Task.objects.all()
                return render(request, "crm_main/task_list_ajax.html", context)


class CreateEvent(LoginRequiredView):


    def get(self, request):        
        # feadback = get_object_or_404(Feadback, pk=feadback_id)
        datetime = request.GET.get("datetime")
        duration = time(1, 0)
        feadback_form = FeadbackForm(initial={})
        event_form = EventForm(initial={'date_time': datetime, 'duration': duration})
        price_form = PriceForm(initial={'discount': 0})

        context = {}
        context["feadback_form"] = feadback_form
        context["event_form"] = event_form
        context["price_form"] = price_form
        return render(request, "create_event.html", context)

    def post(self, request):
        feadback_form = FeadbackForm(request.POST)
        event_form = EventForm(request.POST)
        price_form = PriceForm(request.POST)
        print(price_form)
        if event_form.is_valid() and feadback_form.is_valid():
            feadback_data = feadback_form.cleaned_data
            price_data = price_form.cleaned_data
            client_data = feadback_form.cleaned_data.copy()
            del client_data['wish']
            client_obj, created = Client.objects.get_or_create(tel=client_data['tel'], defaults=client_data)
            feadback_data["has_event"] = True
            event_data = event_form.cleaned_data
            feadback = Feadback.objects.create(**feadback_data)
            price = Price.objects.create(**price_data)
            event_data["feadback"] = feadback
            event_data["price"] = price
            event_data["client"] = client_obj
            q1 = Q(date_time__gte=event_data["date_time"])
            q2 = Q(date_time__lt=(event_data["date_time"] + timedelta(hours=event_data["duration"].hour, minutes=event_data["duration"].minute)))
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
        week_periods = Week(event_list=EventList.eventsOnweek())
        context["week_periods"] = week_periods
        return render(request, "transfer_event_calendar.html", context)


class DeleteEvent(LoginRequiredView):


    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        context = {"event": event}
        return render(request, "delete_event.html", context)

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        if request.POST.get("submit") == "yes":
            event.delete()
            return redirect('/crm/')
        elif request.POST.get("submit") == "no":
            return redirect('/crm/event/%s/'%event_id)
        # data = {}
        
        # for f in Event._meta.get_fields():
        #     if not f.auto_created:
        #         data[f.name] = getattr(event, f.name)
        # # print(type(data["feadback"]))
        # # return HttpResponse(type(data["feadback"]))
        # # CanceledEvent.objects.create()
        # # obj, created = CanceledEvent.objects.update_or_create(defaults=data)
        # event.delete()
        # # return HttpResponse(obj)
        return redirect('/crm/')


class DeleteResult(LoginRequiredView):


    def get(self, request, event_id, result_id):
        result = get_object_or_404(Result, pk=result_id)
        context = {"result": result}
        return render(request, "delete_result.html", context)

    def post(self, request, event_id, result_id):
        result = get_object_or_404(Result, pk=result_id)
        if request.POST.get("submit") == "yes":
            result.delete()
        
        return redirect('/crm/event/%s/'%event_id)


def transferEvent(request, event_id):
    datetime = request.GET.get("datetime")
    event = get_object_or_404(Event, pk=event_id)
    data = {"date_time" : datetime}
    obj, created = Event.objects.update_or_create(pk=event_id, defaults=data)
    return redirect('/crm/')


def searchFeadback(request):
    pass


def feadbackBar(request):
    
    if request.method== "POST" and request.is_ajax():
        context = {}
        if request.POST.get("filter_type") == "all":
            feadback_list_inwork = Feadback.objects.filter(has_event=False).order_by('date')
            feadback_list_done = Feadback.objects.filter(has_event=True).order_by('-date')
            feadback_list = list(feadback_list_inwork)+list(feadback_list_done)
            context["feadback_list"] = feadback_list
            return render(request, "crm_main/feadback_list_ajax.html", context)

        elif request.POST.get("filter_type") == "to_work":
            feadback_list = Feadback.objects.filter(has_event=False).order_by('date')
            context["feadback_list"] = feadback_list
            return render(request, "crm_main/feadback_list_ajax.html", context)

        elif request.POST.get("filter_type") == "processed":
            feadback_list = Feadback.objects.filter(has_event=True).order_by('-date')
            context["feadback_list"] = feadback_list
            return render(request, "crm_main/feadback_list_ajax.html", context)


def taskBar(request):
    if request.method == "POST" and request.is_ajax():
        context = {}
        all_tasks = Task.objects.all()
        print("all tasks")
        print(all_tasks)

        if request.POST.get("filter_type") == "all":
            task_list_inwork = all_tasks.filter(done=False)
            print(task_list_inwork)
            if task_list_inwork:
                task_list_inwork = task_list_inwork.order_by('date')
            else:
                task_list_inwork = []

            task_list_done = all_tasks.filter(done=True)
            print(task_list_done)
            if task_list_done:
                task_list_done = task_list_done.order_by('-date')
            else:
                task_list_done = []

            task_list = list(task_list_inwork) + list(task_list_done)
            print(task_list)
            context["task_list"] = task_list
            return render(request, "crm_main/task_list_ajax.html", context)

        elif request.POST.get("filter_type") == "on_day":
            task_list_inwork = QueryByPeriod.queryOnday(all_tasks.filter(done=False))
            print(task_list_inwork)
            if task_list_inwork:
                task_list_inwork = task_list_inwork.order_by('date')
            else:
                task_list_inwork = []

            task_list_done = QueryByPeriod.queryOnday(all_tasks.filter(done=True))
            print(task_list_done)
            if task_list_done:
                task_list_done = task_list_done.order_by('-date')
            else:
                task_list_done = []

            task_list = list(task_list_inwork) + list(task_list_done)
            context["task_list"] = task_list
            return render(request, "crm_main/task_list_ajax.html", context)

        elif request.POST.get("filter_type") == "on_week":

            task_list_inwork = QueryByPeriod.queryOnweek(all_tasks.filter(done=False))
            print(task_list_inwork)
            if task_list_inwork:
                task_list_inwork = task_list_inwork.order_by('date')
            else:
                task_list_inwork = []

            task_list_done = QueryByPeriod.queryOnweek(all_tasks.filter(done=True))
            print(task_list_done)
            if task_list_done:
                task_list_done = task_list_done.order_by('-date')
            else:
                task_list_done = []

            task_list = list(task_list_inwork) + list(task_list_done)
            context["task_list"] = task_list
            return render(request, "crm_main/task_list_ajax.html", context)

        elif request.POST.get("filter_type") == "on_month":

            task_list_inwork = QueryByPeriod.queryOnmonth(all_tasks.filter(done=False))
            print(task_list_inwork)
            if task_list_inwork:
                task_list_inwork = task_list_inwork.order_by('date')
            else:
                task_list_inwork = []

            task_list_done = QueryByPeriod.queryOnmonth(all_tasks.filter(done=True))
            print(task_list_done)
            if task_list_done:
                task_list_done = task_list_done.order_by('-date')
            else:
                task_list_done = []

            task_list = list(task_list_inwork) + list(task_list_done)
            context["task_list"] = task_list
            return render(request, "crm_main/task_list_ajax.html", context)


def changeWeekCalendar(request):
    context = {}
    if request.method== "POST" and request.is_ajax():
        if request.POST.get("go_to_week") == "prev":
            print(request.POST.get("start_date"))
            start_date = request.POST.get("start_date")
            start_date = start_date.split("-")
            min_datetime = datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))-timedelta(days=7)
            week_periods = Week(event_list=EventList.eventsOnweek(min_datetime), date_time=min_datetime)
            context["week_periods"] = week_periods
            print(week_periods)
            if request.POST.get("transfer_event"):
                context["event_id"] = request.POST.get("event_id")
                return render(request, "transfer_event_week_calendar.html", context)
            return render(request, "crm_calendar/week_calendar.html", context)

        elif request.POST.get("go_to_week") == "next":
            print(request.POST.get("start_date"))
            start_date = request.POST.get("start_date")
            start_date = start_date.split("-")
            min_datetime = datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))+timedelta(days=7)
            week_periods = Week(event_list=EventList.eventsOnweek(min_datetime), date_time=min_datetime)
            context["week_periods"] = week_periods
            print(week_periods)
            # print(request.POST.get("transfer_event"))
            if request.POST.get("transfer_event"):
                context["event_id"] = request.POST.get("event_id")
                return render(request, "transfer_event_week_calendar.html", context)
            return render(request, "crm_calendar/week_calendar.html", context)


def timeView(request):
    min_datetime = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.weekday(datetime.now(timezone.utc))))
    max_datetime = min_datetime+timedelta(days=7)
    
    # return HttpResponse(max_d)
    return HttpResponse(datetime.combine(min_datetime, datetime.min.time()))

def updateTotalPaid(request):
    clients = Client.objects.all()
    pays = Pay.objects.all()
    for client in clients:
        client_pays = pays.filter(client=client)
        client.total_paid =sum((pay.pay for pay in client_pays))
        client.save()
    return redirect("/crm/")