from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.core.validators import validate_email
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from yeureul import statics_variables
from yeureul.utils_functions import ads_are_similar
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.conf import settings as conf_settings
from django.contrib.auth.models import User
from .models import Showroom
from ads.documents import AdDocument
import uuid
from django.core.paginator import Paginator
from elasticsearch_dsl.query import Q
from urllib.parse import quote_plus
from . import forms
from django.contrib.auth import login, logout, authenticate
from yeureul.models import UserInfo


def showrooms(request):
    return render(request, 'showrooms/index.html')


@transaction.atomic
def registration(request):
    """Register showroom"""
    # no need to login if user is already authenticated
    if request.user.is_authenticated:
        return redirect('index')

    # redirection link
    redirect_to = request.GET.get('next', '/')

    if request.method == 'POST':
        form = forms.ShowroomRegistrationForm(data=request.POST)
        if form.is_valid():
            email = form.data['email']
            email = email.lower()
            showroom_name = form.data['showroom_name']
            password = form.data['password']
            user = User.objects.filter(email=email)
            if not user:
                last_id = User.objects.order_by('-id')[0].pk
                username = email.split("@")[0] + str(last_id)
                user = User.objects.create_user(username=username, email=email, password=password)
                UserInfo.objects.create(user=user, creation_date=timezone.now(), user_type='T')
                Showroom.objects.create(name=showroom_name, email=email, user=user)
                login(request, user)

                return redirect(redirect_to)
        else:
            return render(request, 'showrooms/registration.html', {'form': form, 'redirect_to': redirect_to})
    else:
        form = forms.ShowroomRegistrationForm()
    return render(request, 'showrooms/registration.html', {'form': form, 'redirect_to': redirect_to})
