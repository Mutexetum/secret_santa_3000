# -*- coding: utf-8 -*-

import datetime
import hashlib
import json
import logging
import random
import re

import pytz
import requests


from django.conf import settings as settings_conf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from .models import User_s_santa, Notification, States
from telegram import Bot
from .helpers import match_users, dismatch, application_closed
from .telegrambot import send_userinfo_to_santas




def index(request):
    return redirect('send-notification')


class Notifications(View):
    def get(self, request):
        notifications = Notification.objects.all()
        return render(request, 'bot/index.html', {"notifications": notifications})

    def post(self, request):
        print(request.POST)
        bot = Bot(settings_conf.TELEGRAM_TOKEN)
        message = request.POST.get("message", None)
        if message is not None and message != "":
            bot.send_message(chat_id="29286513", text=message)
            Notification.objects.create(text=message)
        return redirect('send-notification')


class Santas(View):
    def get(self, request):
        santas = User_s_santa.objects.all()
        return render(request, 'bot/santas.html', {"santas": santas,
                                                   "application_closed": application_closed()})

    def post(self, request):
        return redirect('santas')


class Start_matching(View):
    def get(self, request):
        match_users()
        return redirect('santas')

    def post(self, request):
        return redirect('santas')


class Dismatch(View):
    def get(self, request):
        dismatch()
        return redirect('santas')

    def post(self, request):
        return redirect('santas')


class Send_target_data_to_santa(View):
    def get(self, request):
        send_userinfo_to_santas()
        return redirect('santas')

    def post(self, request):
        return redirect('santas')


class Toggle_application_period_status(View):
    def get(self, request):
        states = States.objects.all().first()
        if states is None:
            states = States.objects.create()

        if states.application_closed:
            states.application_closed = False
            states.save()
        else:
            states.application_closed = True
            states.save()

        return redirect('santas')

    def post(self, request):
        return redirect('santas')
