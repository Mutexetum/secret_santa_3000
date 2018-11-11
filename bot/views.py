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
from .models import User_s_santa, Notification
from telegram import Bot




def index(request):
    notifications = Notification.objects.all()
    return render(request, 'bot/index.html', {"notifications": notifications})


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
