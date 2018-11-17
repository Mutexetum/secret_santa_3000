"""ss_3000 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from .views import (Dismatch, Notifications, Santas, Send_target_data_to_santa,
                    Start_matching, index, Toggle_application_period_status)

urlpatterns = [
   path('', login_required(index), name='index'),
   path('send-notification', login_required(Notifications.as_view()), name='send-notification'),
   path('santas', login_required(Santas.as_view()), name='santas'),
   path('start-matching', login_required(Start_matching.as_view()), name='start_matching'),
   path('dismatch', login_required(Dismatch.as_view()), name='dismatch'),
   path('send-target-data-to-santa', login_required(Send_target_data_to_santa.as_view()), name='send_target_data_to_santa'),
   path('toggle-application-period-status', login_required(Toggle_application_period_status.as_view()), name='toggle_application_period_status'),
]
