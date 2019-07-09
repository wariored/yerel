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
from ads.models import Ad, Category, AdFile, Location
from yeureul import utils_functions
from .documents import ShowroomDocument


def showrooms(request):
    all_showrooms = Showroom.objects.all().order_by('-is_premium', '-is_sponsored')
    text_to_search = request.GET.get('text_to_find')
    page = request.GET.get('page')
    if text_to_search == 'None':
        text_to_search = None
    if text_to_search:
        found_showroom = []
        search = ShowroomDocument.search()
        search = search.query(
            Q('match', name=text_to_search) |
            Q('match', website=text_to_search) |
            Q('match', description=text_to_search)
        )

        for ad in search:
            found_showroom.append(ad.id)
        all_showrooms = all_showrooms.filter(id__in=found_showroom)
        split_text = text_to_search.split(' ')
        for word in split_text:
            found_showrooms_name_by_split = Showroom.objects.filter(name__icontains=word).order_by('-is_premium',
                                                                                                   '-is_sponsored')
            found_showrooms_description_by_split = Showroom.objects.filter(description__icontains=word)
            all_showrooms = all_showrooms | found_showrooms_name_by_split | found_showrooms_description_by_split

    all_showrooms = all_showrooms.distinct()
    paginator = Paginator(all_showrooms, 12)
    all_showrooms = paginator.get_page(page)

    return render(request, 'showrooms/index.html', {'showrooms': all_showrooms, 'text_to_search': text_to_search})


@transaction.atomic
def registration(request):
    """Register showroom"""
    # no need to login if user is already authenticated
    if request.user.is_authenticated:
        return redirect('index')

    # redirection link
    redirect_to = request.GET.get('next', '/')
    error = False
    error_message = ''
    if request.method == 'POST':
        form = forms.ShowroomRegistrationForm(data=request.POST)
        if form.is_valid():
            email = form.data['email']
            email = email.lower()
            showroom_name = form.data['showroom_name']
            password = form.data['password']
            user = User.objects.filter(email=email)
            # started transaction
            sid = transaction.savepoint()
            if not user:
                last_id = User.objects.order_by('-id')[0].pk
                username = email.split("@")[0] + str(last_id + 1)
                user = User.objects.create_user(username=username, email=email, password=password, first_name="shop",
                                                last_name="shop")
                UserInfo.objects.create(user=user, creation_date=timezone.now(), user_type='T', phone_number=7777777)
                try:
                    Showroom.objects.get(name=showroom_name)
                except Showroom.DoesNotExist:
                    Showroom.objects.create(name=showroom_name, email=email, user=user)
                else:
                    error = True
                    error_message = 'name'
                    # rollback
                    transaction.savepoint_rollback(sid)

                if not error:
                    # generate a token with the user as key, key_type="A" is for account Activation
                    uid, token = utils_functions.uid_token_generator(user, key_type="A")
                    url = conf_settings.BASE_URL + "account/validate/%s/%s" % (uid, token)

                    # send email activation to the new user
                    html_message = render_to_string('mails/account_activation_showroom.html',
                                                    {'email': request.user, 'link': url,
                                                     'showroom_name': showroom_name})
                    utils_functions.send_email(html_message=html_message, subject='Yerel Showroom activation',
                                               to=[user.email])
                    # end transaction, save into DB
                    transaction.savepoint_commit(sid)
                    # log in the user
                    login(request, user)

                    return redirect(redirect_to)
            else:
                error_message = 'email'
                return render(request, 'showrooms/registration.html',
                              {'form': form, 'redirect_to': redirect_to, 'error_message': error_message})
    else:
        form = forms.ShowroomRegistrationForm()
    return render(request, 'showrooms/registration.html',
                  {'form': form, 'redirect_to': redirect_to, 'error_message': error_message})


def single_showroom(request, id_showroom):
    try:
        showroom = Showroom.objects.get(pk=id_showroom)
    except Showroom.DoesNotExist:
        return Http404

    categories_t = Category.objects.filter(category_type='T')

    page = request.GET.get('page')
    category_id = request.GET.get('category', None)
    selected_condition = request.GET.get('condition', None)
    subcategories_id = request.GET.get('subcategories', None)
    min_max_price = request.GET.get('min_max_price', None)
    price_order_type = request.GET.get('price_order', None)
    location = request.GET.get('location', None)
    text_to_search = request.GET.get('text_to_find', None)
    selected_category = None
    selected_subcategories = None
    filter_by_price = None
    selected_location = None

    if text_to_search:
        text_to_search = text_to_search.strip()

    if category_id:
        try:
            selected_category = Category.objects.get(pk=category_id)
            selected_ads = Ad.manager_object.can_be_shown_to_public().filter(
                subcategory__in=selected_category.subcategories.all(), ad_user__user__id=showroom.user.id).order_by(
                '-creation_date')
        except Category.DoesNotExist:
            raise Http404
    else:
        selected_ads = Ad.manager_object.can_be_shown_to_public().filter(ad_user__user__id=showroom.user.id).order_by(
            '-creation_date')

    if text_to_search:
        found_ads = []
        search = AdDocument.search()
        search = search.query(
            Q('match', title=text_to_search) |
            Q('match', description=text_to_search)
        )
        for ad in search:
            found_ads.append(ad.id)

        selected_ads = selected_ads.filter(id__in=found_ads)
        split_text = text_to_search.split(' ')
        for word in split_text:
            found_ads_title_by_split = Ad.manager_object.can_be_shown_to_public().filter(title__icontains=word,
                                                                                         ad_user__user__id=showroom.user.id)
            found_ads_description_by_split = Ad.manager_object.can_be_shown_to_public().filter(
                description__icontains=word, ad_user__user__id=showroom.user.id)
            selected_ads = selected_ads | found_ads_title_by_split | found_ads_description_by_split

        selected_ads = selected_ads.distinct()

    if selected_condition:
        selected_ads = selected_ads.filter(condition=selected_condition)

    if subcategories_id:
        if subcategories_id not in ['all_categories', 'other_categories']:
            subcategories_id = subcategories_id.split(',')
            selected_ads = selected_ads.filter(subcategory__id__in=subcategories_id)
            selected_subcategories = Category.objects.filter(id__in=subcategories_id)
    if min_max_price:
        min_max_price = min_max_price.split(",")
        if len(min_max_price) == 2:
            min_price = min_max_price[0]
            max_price = min_max_price[1]
            if not min_price:
                min_price = 0.0
            if not max_price:
                max_price = 2e31
            try:
                min_price = float(min_price)
                max_price = float(max_price)
            except ValueError:
                pass
            else:
                if min_price <= max_price:
                    selected_ads = selected_ads.filter(price__range=(min_price, max_price))
                    if max_price == 2e31:
                        max_price = ''
                    filter_by_price = {
                        'min': min_price,
                        'max': max_price
                    }
    if price_order_type:
        if price_order_type == 'low':
            selected_ads = selected_ads.order_by('price')
        elif price_order_type == 'high':
            selected_ads = selected_ads.order_by('-price')

    if location:
        if location != 'all_locations':
            selected_ads = selected_ads.filter(location__id=location)
            try:
                selected_location = Location.objects.get(pk=location)
            except Location.DoesNotExist:
                pass
    all_locations = Location.objects.all()
    paginator = Paginator(selected_ads, 12)
    selected_ads = paginator.get_page(page)
    return render(request, 'showrooms/single_showroom.html',
                  dict(showroom=showroom, categories_t=categories_t, selected_category=selected_category,
                       selected_ads=selected_ads,
                       selected_condition=selected_condition, selected_subcategories=selected_subcategories,
                       filter_by_price=filter_by_price, price_order_type=price_order_type,
                       selected_location=selected_location, text_to_search=text_to_search, all_locations=all_locations))
