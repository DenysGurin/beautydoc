import random
import re
import json
from datetime import datetime, timedelta, timezone

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
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from .forms import FeadbackForm, ReviewForm#, FeadbackForm1
from .models import Client, Feadback, Portfolio, Review, ServiceCategory, Service

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

bot_configuration = BotConfiguration(
    name='PythonSampleBot',
    avatar='http://localhost:8000/avatar.jpg',
    auth_token='460ef98946f427fd-004f950cd01a76f3-326b0d5bf160a707'
)
viber = Api(bot_configuration)



class Main(View):
    def __init__(self):
        View.__init__(self)
        portfolio = Portfolio.objects.all()
        reviews = Review.objects.all().order_by("-id")
        service_categories = ServiceCategory.objects.all().order_by("-id")
        services = Service.objects.all()
        self.context = {"portfolio": portfolio, 
                        "reviews": reviews[:3],
                        "reviews_num": reviews.count(),
                        "service_categories": service_categories,
                        "services": services,
                        }

        if service_categories.count() > 0:
            col_size = 12//service_categories.count()

            self.context["col_size"] = "s%s"%col_size

        self.num_photo = 3

    def make_pagination(self, request, some_list=None, num_items=2):
        paginator = Paginator(some_list, num_items) 
        request = getattr(request, request.method)
        page = request.get('page')
        try:
            pags = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            pags = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            pags = paginator.page(paginator.num_items)
        return pags

    def get(self, request):
        self.context['portfolio_pags'] = Main.make_pagination(self, request, self.context["portfolio"], self.num_photo)
        self.context['feadback_form'] = FeadbackForm()
        self.context['review_form'] = ReviewForm()
        
        return render(request, "main.html", self.context)

    def post(self, request):

        feadback_form = FeadbackForm(request.POST)
        review_form  = ReviewForm(request.POST)
        # check whether it's valid:
        try:
            submit_flag = request.POST["submit"]

            if submit_flag == "feadback" and feadback_form.is_valid():
                first = feadback_form.cleaned_data['first']
                last = feadback_form.cleaned_data['last']
                tel = feadback_form.cleaned_data['tel']
                wish = feadback_form.cleaned_data['wish']
                email = feadback_form.cleaned_data['email']
                # form.save()
                client_data = feadback_form.cleaned_data
                del client_data['wish']

                client_obj, created = Client.objects.get_or_create(tel=tel, defaults=client_data)

                feadback_data = feadback_form.cleaned_data
                feadback_data["client"] = client_obj

                Feadback.objects.create(**feadback_data)

                #print(form.cleaned_data.values())
                send_mail(
                    'Новая запись',
                    'Клиент: %s %s\nНомер телефона: %s\nИнформация: %s\nEmail: %s\n'%(first,
                                                                                      last,
                                                                                      tel,
                                                                                      wish,
                                                                                      email,
                    ),
                    settings.EMAIL_HOST_USER,
                    ['gurindenys@gmail.com'],
                    fail_silently=False,
                )
                return HttpResponse('/feadback_form/')

            elif submit_flag == "review" and review_form.is_valid():
                Review.objects.create(**review_form.cleaned_data)
                return HttpResponse('/review_form/')
        except MultiValueDictKeyError:
            pass

        if request.is_ajax():
            portfolio_pags = Main.make_pagination(self, request, self.context["portfolio"], self.num_photo)

            return render(request, "portfolio.html", {"portfolio_pags": portfolio_pags})
            
            # return render_to_response("portfolio.html", {"portfolio_pags": portfolio_pags})

        return HttpResponse(review_form)

def more_reviews(request):
    if request.is_ajax():
        num = request.POST['num']
        print(num)
        reviews = Review.objects.all().order_by("-id")[:int(num)]
        return render(request, "reviews.html", {"reviews": reviews})
    else:
        return Http404


class Price(View):
    
    def __init__(self):
        View.__init__(self)
        service_categories = ServiceCategory.objects.all().order_by("-id")
        self.context = {"service_categories": service_categories,
                        }

        if service_categories.count() > 0:
            cat_size = 100//service_categories.count()

            self.context["cat_size"] = "%s"%cat_size


    def get(self, request, category, service=None):
        print(service)
        self.context['services'] = Service.objects.filter(service_category=category)

        if self.context['services'].count() > 0:
            serv_size = 100//self.context['services'].count()
            self.context["serv_size"] = "%s"%serv_size

        self.context['category_id'] = int(category)
        if self.context['services'].count() > 0:
            if service == "":
                service = self.context['services'][0].id
                print(service)
            self.context['service_id'] = int(service)

        return render(request, "price.html", self.context)