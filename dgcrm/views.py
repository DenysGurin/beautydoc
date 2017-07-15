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


from .forms import EventForm, ResultForm, PayForm, DetailedEventForm, SearchForm, FeadbackForm, SearchFeadbackForm, TaskForm, PriceForm, ClientForm
from main.models import ServiceCategory, Service, DetailedService
from .models import Event, Client, Feadback, Task, Result, CanceledEvent, Pay, Price

from django.db.models import F, Q

from .Day import Day


def dayPeriods(hour=9, minute=0, second=0):
    start_day = datetime.time(hour, minute, second)

class QueryByPeriod(object):

    @classmethod
    def byDay(cls, min_datetime):
        if not min_datetime:
            min_date = datetime.date(timezone.now())
        else:
            min_date = min_date.date()
        max_date = min_date + timedelta(days=1)
        q_object = Q()
        q_object &= Q(date__gte=min_date)
        q_object &= Q(date__lt=max_date)
        return q_object

    @classmethod
    def byWeek(cls, min_datetime):
        if not min_datetime:
            min_date = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.weekday(datetime.now(timezone.utc))))
        else:
            min_date = datetime.date(min_date-timedelta(days=datetime.weekday(min_datetime)))
        max_date = min_date+timedelta(days=7)
        q_object = Q()
        q_object &= Q(date__gt=min_date)
        q_object &= Q(date__lt=max_date)
        return q_object

    @classmethod
    def byMonth(cls, min_datetime):
        if not min_datetime:
            min_date = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.now(timezone.utc).day-1))
        else:
           min_date = datetime.date(min_date-timedelta(days=min_date.day-1))
        
        max_datetime = date(int(min_date.year), int(min_date.month)+1, 1)
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
        return events.order_by('date')

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
        if (eve_st_gte_per_st and eve_st_lt_per_en) or (eve_st_lt_per_st and eve_en_gt_per_en) or(eve_en_gt_per_en and eve_en_lte_per_en) or (eve_en_gt_per_st and eve_en_lte_per_en):
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

    @classmethod
    def addClientToEvent(self):
        clients = Client.objects.all()
        events = Event.objects.all()
        for event in events:
            if not event.client:
                tel = event.feadback.tel
                for client in clients:
                    if client.tel == tel:
                        event.client = client
                        event.save()


    def get(self, request):
        if request.user.is_authenticated:
            # CrmMain.addClientToEvent(self)
            context = {"user": request.user}
            serch_form = SearchForm()#initial={'search': '%sпоиск'%search_icon})
            serch_feadback_form = SearchFeadbackForm()
            feadback_list_inwork = Feadback.objects.filter(has_event=False).order_by('id')
            feadback_list_done = Feadback.objects.filter(has_event=True).order_by('-id')
            feadback_list = list(feadback_list_inwork)+list(feadback_list_done)

            print(Task.objects.filter(done=False))
            task_list_inwork = QueryByPeriod.queryOnday(Task.objects.filter(done=False))
            # task_list_done = QueryByPeriod.queryOnday(Task.objects.filter(done=True))
            if task_list_inwork != None:# or task_list_done != None:
                task_list = list(task_list_inwork)#+list(task_list_done)
                context["task_list"] = task_list

            periods = Day(event_list=EventList.eventsOnday())
            week_periods = Week(event_list=EventList.eventsOnweek())
            client_list = Client.objects.all()

            # return HttpResponse(EventList.eventsOnday(self))
            context["serch_form"] = serch_form
            context["serch_feadback_form"] = serch_feadback_form
            context["feadback_list"] = feadback_list
            
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


class DetailedEvent(View):
    @staticmethod
    def updateModelInstanceData(model_inst, data_dict):
        for key in data_dict.keys():
            setattr(model_inst, key, data_dict[key])
            model_inst.save()
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        event_period = EventPeriod(event)
        client = event.client
        event_list = Event.objects.filter(client=client).order_by("-date_time")
        result_list = Result.objects.filter(client=client)
        default_data = client
        
        client_form = ClientForm(initial=client.__dict__)
        detailed_event_form = DetailedEventForm(initial={'status': event.status, 'initial': "Изменить статус"})
        # print(event_period.is_in_past)
        if event_period.is_in_past:
            # print(dir(detailed_event_form.fields["status"]))
            # print(detailed_event_form.fields["status"].choices)
            detailed_event_form.fields["status"].choices = (("successful", 'сделано'),
                                                            ("failed", 'отменился'),
                                                            ("contact", 'связаться'))
        else:
            detailed_event_form.fields["status"].choices = (("in_progress", 'ожидается'),
                                                            ("successful", 'сделано'),
                                                            ("failed", 'отменился'),
                                                            ("contact", 'связаться'))


        price_form = PriceForm()
        result_form = ResultForm(initial={#'client': event.client,
                                          #'detailed_service': event.detailed_service, 
                                          'date': (event.date_time + timedelta(hours=event.duration.hour, minutes=event.duration.minute))})
        pay_form = PayForm(initial={#'client': event.client,
                                    #'detailed_service': event.detailed_service, 
                                    'date_time': (event.date_time + timedelta(hours=event.duration.hour, minutes=event.duration.minute))})
        context = {}
        context["event_id"] = int(event_id)
        context["event_period"] = event_period
        context["event"] = event
        context["client"] = client
        context["event_list"] = event_list
        context["client_form"] = client_form
        context["detailed_event_form"] = detailed_event_form
        context["price_form"] = price_form
        context["result_form"] = result_form
        context["pay_form"] = pay_form
        return render(request, "detailed_event.html", context)

    def post(self, request, event_id):
        result_form = ResultForm(request.POST, request.FILES)
        pay_form = PayForm(request.POST)
        detailed_event_form = DetailedEventForm(request.POST)
        client_form = ClientForm(request.POST)

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
            print(client_data)
            DetailedEvent.updateModelInstanceData(event.client, client_data)
            # event.status = detailed_event_form.cleaned_data["status"]
            event.save()
            

        if detailed_event_form.is_valid() and request.POST.get("submit") == None:

            detailed_event_data = detailed_event_form.cleaned_data
            event.status = detailed_event_form.cleaned_data["status"]
            # print(detailed_event_form.cleaned_data["status"])
            event.save()
            
            # return render(request, "create_event.html", {})
            
        return redirect("/crm/event/%s"%event_id)

class DetailedClient(View):

    def get(self, request, client_id):
        client = get_object_or_404(Client, pk=client_id)
        event_list = Event.objects.filter(client=client).order_by("-date_time")
        result_list = Result.objects.filter(client=client)
        # detailed_service_list = ClientServiceLinker.objects.filter(client=client)
        # print((timezone.now()))
        default_data = client

        client_form = ClientForm(default_data)
        detailed_event_form = DetailedEventForm(initial={})
        price_form = PriceForm(initial={})
        result_form = ResultForm(initial={#'client': event.client,
                                          #'detailed_service': event.detailed_service, 
                                          'date': timezone.now()})
        pay_form = PayForm(initial={#'client': event.client,
                                    #'detailed_service': event.detailed_service, 
                                    'date_time': timezone.now()})
        context = {}
        context["client"] = client
        context["event_list"] = event_list
        context["result_list"] = result_list
        context["client_form"] = client_form
        context["detailed_event_form"] = detailed_event_form
        context["price_form"] = price_form
        context["result_form"] = result_form
        context["pay_form"] = pay_form
        # context["detailed_service_list"] = detailed_service_list
        return render(request, "detailed_client.html", context)


class CreateTask(View):

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

class CreateEvent(View):

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

class DeleteEvent(View):
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


class DeleteResult(View):
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
            return render(request, "week_calendar.html", context)

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
            return render(request, "week_calendar.html", context)


def timeView(request):
    min_datetime = datetime.date(datetime.now(timezone.utc)-timedelta(days=datetime.weekday(datetime.now(timezone.utc))))
    max_datetime = min_datetime+timedelta(days=7)
    
    # return HttpResponse(max_d)
    return HttpResponse(datetime.combine(min_datetime, datetime.min.time()))