import random
import re
import json
from datetime import datetime, timedelta, timezone

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.views import View
from django.views.generic.detail import DetailView
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from .forms import FeadbackForm, ReviewForm#, FeadbackForm1
from .models import Client, Feadback, Portfolio, Review

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
        reviews = Review.objects.all().order_by("date")
        self.context = {"portfolio": portfolio, 
                        "reviews": reviews,
                        }

    def make_pagination(self, request, some_list=None, num_items=2):
        paginator = Paginator(some_list, num_items) 
        page = request.GET.get('page')
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
        self.context['portfolio_pags'] = Main.make_pagination(self, request, self.context["portfolio"], 6)
        self.context['feadback_form'] = FeadbackForm()
        self.context['review_form'] = ReviewForm()

        return render(request, "main.html", self.context)

    def post(self, request):

        feadback_form = FeadbackForm(request.POST)
        review_form  = ReviewForm(request.POST)
        # check whether it's valid:
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
            # send_mail(
            #     'Новая запись',
            #     'Клиент: %s %s\nНомер телефона: %s\nИнформация: %s\nEmail: %s\n'%(first,
            #                                                                       last,
            #                                                                       tel,
            #                                                                       wish,
            #                                                                       email,
            #     ),
            #     settings.EMAIL_HOST_USER,
            #     ['gurindenys@gmail.com'],
            #     fail_silently=False,
            # )
            return HttpResponse('/feadback_form/')

        elif submit_flag == "review" and review_form.is_valid():
            Review.objects.create(**review_form.cleaned_data)
            return HttpResponse('/review_form/')
        #return HttpResponse(form.cleaned_data.values())
        return HttpResponse(review_form)