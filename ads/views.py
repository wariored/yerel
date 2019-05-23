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
from .models import Ad, AdFile, AdUser, Category, Location, HistoricalFeatured, AdFeatured, Alert, Signal
from ads.documents import AdDocument
import uuid
from django.core.paginator import Paginator
from elasticsearch_dsl.query import Q
from urllib.parse import quote_plus
from .utils.utils_functions import unique_ad_random_code_generator


def categories(request):
    categories_t = Category.objects.filter(category_type='T')
    return render(request, 'ads/categories_pages/categories.html',
                  dict(categories_t=categories_t),
                  )


def create_post(request):
    categories_t = Category.objects.filter(category_type='T')
    locations = Location.objects.all().order_by('name')
    create_post_error = request.session.get('create_post_error', None)
    create_post_success = request.session.get('create_post_success', None)
    dict_values = request.session.get('dict_values', None)
    random_code = request.session.get('random_code', '')
    ad_deletion = request.session.get('ad_deletion', None)
    if ad_deletion:
        del request.session['ad_deletion']

    if create_post_error:
        del request.session['create_post_error']
        if create_post_error != 'has_reached_limit' and dict_values:
            del request.session['dict_values']
    elif create_post_success:
        del request.session['create_post_success']
    if random_code != '':
        del request.session['random_code']
    return render(request, 'ads/create_post.html',
                  dict(categories_t=categories_t, locations=locations, create_post_error=create_post_error,
                       create_post_success=create_post_success, dict_values=dict_values, random_code=random_code,
                       ad_deletion=ad_deletion
                       )
                  )


@transaction.atomic
def create_post_verification(request):
    if request.method == 'POST':
        title = request.POST['title']
        category = request.POST['category']
        condition = request.POST['condition']
        price = request.POST['price']
        photos = request.FILES.getlist('photos', None)
        location = request.POST['location']
        description = request.POST['description']
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        phone_number = request.POST.get('phone_number', None)

        if email:
            email = email.lower()
        if price == '':
            price = 0

        # check if user has reached ads limit
        if request.user.is_authenticated:
            if not request.user.info.activated_account:
                request.session['create_post_error'] = 'activation'
                return redirect('ads:create_post')
            ad_user = AdUser.objects.filter(email=request.user.email).first()
        else:
            ad_user = AdUser.objects.filter(email=email).first()
        if ad_user:
            if ad_user.has_reached_ads_limit(request):
                request.session['create_post_error'] = 'has_reached_limit'
                return redirect('ads:create_post')

        dict_values = dict(title=title, price=price,
                           description=description, name=name, email=email, phone_number=phone_number
                           )
        if not title or len(title) > 50:
            request.session['create_post_error'] = 'title'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')
        if not category:
            request.session['create_post_error'] = 'category'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')
        else:
            try:
                Category.objects.get(pk=category, category_type='B')
            except Category.DoesNotExist:
                request.session['create_post_error'] = 'category'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
        if not condition or condition not in ['N', 'U']:
            request.session['create_post_error'] = 'condition'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')
        if len(str(price)) > 20:
            request.session['create_post_error'] = 'price'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')
        else:
            try:
                price = float(price)
                price = abs(price)
            except ValueError:
                request.session['create_post_error'] = 'price'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
        if photos:
            if len(photos) > statics_variables.MAX_PHOTOS:
                request.session['create_post_error'] = 'photos'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
            check_photos = ['error' for p in photos if p.size > int(statics_variables.MAX_SIZE)]
            if 'error' in check_photos:
                request.session['create_post_error'] = 'photos'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
        if not location:
            request.session['create_post_error'] = 'location'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')
        else:
            try:
                Location.objects.get(pk=location)
            except Location.DoesNotExist:
                request.session['create_post_error'] = 'location'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
        if not description or len(description) not in range(20, 2000):
            request.session['create_post_error'] = 'description'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')

        subcategory = Category.objects.get(pk=category)
        location = Location.objects.get(pk=location)
        # started transaction
        sid = transaction.savepoint()
        if not request.user.is_authenticated:
            if not name or len(name) > 50:
                request.session['create_post_error'] = 'name'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
            try:
                validate_email(email)
            except:
                request.session['create_post_error'] = 'email'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')

            if len(phone_number) != 9:
                request.session['create_post_error'] = 'phone_number'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
            try:
                int(phone_number)
            except ValueError:
                request.session['create_post_error'] = 'phone_number'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
            try:
                ad_user = AdUser.objects.get(email=email)
            except AdUser.DoesNotExist:
                ad_user = AdUser.objects.create(given_name=name, phone_number=phone_number, email=email)
            else:
                ad_user.phone_number = phone_number
                ad_user.given_name = name
                ad_user.save()
        else:
            user = request.user
            if not user.first_name or not user.last_name:
                request.session['create_post_error'] = 'name'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
            if not user.info.phone_number:
                request.session['create_post_error'] = 'phone_number'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
            given_name = user.first_name + ' ' + user.last_name
            try:
                ad_user = AdUser.objects.get(email=user.email)
            except AdUser.DoesNotExist:
                ad_user = AdUser.objects.create(user=user, email=user.email, given_name=given_name,
                                                phone_number=user.info.phone_number)

        ad = Ad.objects.create(title=title, price=price, condition=condition, description=description,
                               subcategory=subcategory, location=location, ad_user=ad_user,
                               creation_date=timezone.now()
                               )
        if photos:
            for photo in photos:
                try:
                    Image.open(photo)
                    AdFile.objects.create(ad=ad, media=photo)
                except:
                    # rollback the transaction
                    transaction.savepoint_rollback(sid)
                    request.session['create_post_error'] = 'photo_format'
                    request.session['dict_values'] = dict_values
                    return redirect('ads:create_post')
        if request.user.is_authenticated:
            ad.is_active = True
            ad.save()
            # end transaction, save into DB
            transaction.savepoint_commit(sid)
            # return the ad view
            return redirect(reverse('ads:single_item', args=(ad.random_url.hex,)))
        ad.random_code = unique_ad_random_code_generator(ad)
        ad.save()
        # user is not login (exits or anonymous), we send him/her a mail admin to validate, delete or edit the post
        url = conf_settings.BASE_URL + "ads/single_item/" + ad.random_url.hex + '/' + ad.random_code + "/"
        html_message = render_to_string('mails/ad_admin_mail.html', {'link': url})
        plain_message = strip_tags(html_message)
        email = EmailMessage("Yerel admin's mail for ad", plain_message, to=[ad_user.email])
        email.send()
        # end transaction, save into DB
        transaction.savepoint_commit(sid)
        # return redirect('ads:single_item', args='')
        request.session['create_post_success'] = 'success'
        request.session['random_code'] = ad.random_code
    return redirect('ads:create_post')


def resend_ad_admin_mail(request, random_code):
    try:
        ad = Ad.objects.get(random_code=random_code)
    except Ad.DoesNotExist:
        raise Http404
    ad_user = ad.ad_user
    url = conf_settings.BASE_URL + "ads/single_item/" + ad.random_url.hex + '/' + ad.random_code + "/"
    html_message = render_to_string('mails/ad_admin_mail.html', {'link': url})
    plain_message = strip_tags(html_message)
    email = EmailMessage("Yerel admin's mail for ad", plain_message, to=[ad_user.email])
    email.send()
    request.session['random_code'] = random_code
    request.session['create_post_success'] = 'success'
    return redirect('ads:create_post')


def update_ad(request, random_url, random_code=''):
    """
    Handle the update of a ad by the aduser
    """
    try:
        if type(random_url) == str:
            random_url = uuid.UUID(random_url)

        ad = Ad.objects.get(random_url=random_url)
        if not request.user.is_authenticated:
            if ad.random_code and ad.random_code != random_code:
                raise Http404
        else:
            if ad.random_code and random_code != '':
                raise Http404

        if not ad.can_be_edited():
            raise Http404
        categories_t = Category.objects.filter(category_type='T')
        locations = Location.objects.all()
        update_ad_error = request.session.get('update_ad_error', None)
        if update_ad_error:
            del request.session['update_ad_error']
        context = {
            'ad': ad,
            'categories_t': categories_t,
            'locations': locations,
            'update_ad_error': update_ad_error,
            'random_code': random_code
        }
    except ValidationError:
        raise Http404
    return render(request, 'ads/update_post.html', context)


@transaction.atomic
def update_ad_verification(request, random_url, random_code=''):
    if request.method == 'POST':
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        images = AdFile.objects.filter(ad=ad)
        category = request.POST['category']
        condition = request.POST['condition']
        price = request.POST['price']
        photos = request.FILES.getlist('photos', None)
        phone_number = request.POST.get('phone_number', None)
        name = request.POST.get('name', None)
        location = request.POST['location']
        description = request.POST['description']
        if not request.user.is_authenticated:
            if ad.random_code and ad.random_code != random_code:
                raise Http404
        else:
            if random_code != '':
                raise Http404
        if not ad.can_be_edited():
            raise Http404

        if price == '':
            price = 0

        if len(str(price)) > 20:
            request.session['update_ad_error'] = 'price'
            if request.user.is_authenticated:
                return redirect(reverse('ads:update_ad', args=(random_url,)))
            return redirect(
                reverse('ads:update_ad', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))
        else:
            try:
                price = float(price)
                price = abs(price)
            except ValueError:
                request.session['update_ad_error'] = 'price'
                if request.user.is_authenticated:
                    return redirect(reverse('ads:update_ad', args=(random_url,)))
                return redirect(
                    reverse('ads:up', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))

        if not description or len(description) not in range(20, 2000):
            request.session['update_ad_error'] = 'description'
            if request.user.is_authenticated:
                return redirect(reverse('ads:update_ad', args=(random_url,)))
            return redirect(
                reverse('ads:update_ad', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))

        if name and len(name) > 50:
            request.session['create_post_error'] = 'name'
            return redirect(
                reverse('ads:update_ad', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))

        if phone_number:
            if len(phone_number) != 9:
                request.session['create_post_error'] = 'phone_number'
                return redirect(
                    reverse('ads:update_ad', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))
            try:
                int(phone_number)
            except ValueError:
                request.session['create_post_error'] = 'phone_number'
                return redirect(
                    reverse('ads:update_ad', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))

        if photos:
            if len(photos) > statics_variables.MAX_PHOTOS:
                request.session['update_ad_error'] = 'photos'
                if request.user.is_authenticated:
                    return redirect(reverse('ads:update_ad', args=(random_url,)))
                return redirect(
                    reverse('ads:single_item', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))
            check_photos = ['error' for p in photos if p.size > int(statics_variables.MAX_SIZE)]
            if 'error' in check_photos:
                request.session['update_ad_error'] = 'photos'
                if request.user.is_authenticated:
                    return redirect(reverse('ads:update_ad', args=(random_url,)))
                return redirect(
                    reverse('ads:update_ad', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))
            for photo in photos:
                try:
                    Image.open(photo)
                except:
                    request.session['create_post_error'] = 'photo_format'
                    if request.user.is_authenticated:
                        return redirect(reverse('ads:update_ad', args=(random_url,)))
                    return redirect(
                        reverse('ads:update_ad',
                                kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))
            images.delete()
            for photo in photos:
                AdFile.objects.create(ad=ad, media=photo)

        ad.description = description
        ad.price = price
        ad.condition = condition
        ad.subcategory = Category.objects.get(pk=category)
        ad.location = Location.objects.get(pk=location)
        if name:
            ad_user = ad.ad_user
            ad_user.given_name = name
            if phone_number:
                ad_user.phone_number = phone_number
            ad_user.save()
            try:
                user = ad_user.user
            except User.DoesNotExist:
                pass
            else:
                split_name = ad_user.given_name.split(' ')
                if len(split_name) != 1:
                    user.last_name = split_name[-1]
                    user.first_name = " ".join(split_name[:-1])
                else:
                    user.first_name = ad_user.given_name
                if phone_number:
                    user_info = user.info
                    user_info.phone_number = phone_number
                    user_info.save()
                user.save()
        ad.save()

        if request.user.is_authenticated:
            return redirect(reverse('ads:single_item', args=(random_url,)))

        return redirect(
            reverse('ads:single_item', kwargs={'random_url': ad.random_url.hex, 'random_code': random_code}))


def single_item(request, random_url, random_code=''):
    try:
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        if ad.is_deleted:
            raise Http404
        if ad.random_code and random_code:
            if ad.random_code != random_code:
                raise Http404
            else:
                if ad.can_be_edited() and not ad.is_active:
                    ad.is_active = True
                    ad.save()
        if request.user.is_authenticated:
            if ad.random_code and random_code != '':
                raise Http404

        share_ad = quote_plus(ad.description)
        if not request.session.get('viewed_post_%s' % random_url, False) and ad.ad_user.user != request.user:
            ad.views_number += 1
            ad.save()
            request.session['viewed_post_%s' % random_url] = True
            request.session.set_expiry(86400)
        if request.user in ad.likes.all():
            liked = True
        else:
            liked = False
        similar_ads = list()
        all_ads = Ad.manager_object.can_be_shown_to_public().exclude(pk=ad.pk).order_by('-update_date')
        for add in all_ads:
            if ads_are_similar(add.description, ad.description):
                similar_ads.append(add)
                if len(similar_ads) == 6:
                    break

        # signal_succes = False
        ad_signal = request.session.get('ad_signal', None)
        if ad_signal:
            del request.session['ad_signal']
        count = ad.likes.count()
        context = {
            'like_count': count,
            'ad_liked': liked,
            'ad': ad,
            'ads_similar': similar_ads,
            'shared_ad': share_ad,
            'random_code': random_code,
            'ad_signal': ad_signal
        }
    except ValidationError:
        raise Http404

    return render(request, 'ads/single_item/single_item.html', context)


def single_item_update(request, random_url):
    try:
        ad = Ad.objects.get(random_url=random_url)
    except ValidationError:
        raise Http404
    return render(request, 'ads/single_item/single_item.html', {'ad': ad})


def single_item_delete(request, random_url):
    try:
        ad = Ad.objects.get(random_url=random_url)
    except ValidationError:
        raise Http404
    return render(request, 'ads/single_item/single_item.html')


def categories_grid(request):
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
                subcategory__in=selected_category.subcategories.all()).order_by(
                '-creation_date')
        except Category.DoesNotExist:
            raise Http404
    else:
        selected_ads = Ad.manager_object.can_be_shown_to_public().order_by('-creation_date')

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
            found_ads_title_by_split = Ad.manager_object.can_be_shown_to_public().filter(title__contains=word)
            found_ads_description_by_split = Ad.manager_object.can_be_shown_to_public().filter(
                description__contains=word)
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

    paginator = Paginator(selected_ads, 12)
    selected_ads = paginator.get_page(page)
    return render(request, 'ads/categories_pages/categories_grid.html',
                  dict(categories_t=categories_t, selected_category=selected_category, selected_ads=selected_ads,
                       selected_condition=selected_condition, selected_subcategories=selected_subcategories,
                       filter_by_price=filter_by_price, price_order_type=price_order_type,
                       selected_location=selected_location, text_to_search=text_to_search))


# handle the ad's like
@login_required
def like_ad(request):
    ad = get_object_or_404(Ad, id=request.POST.get('id'))
    if request.user in ad.likes.all():
        ad.likes.remove(request.user)
        liked = False
    else:
        ad.likes.add(request.user)
        liked = True

    context = {
        'ad_liked': liked,
        'ad': ad,
    }
    if request.is_ajax():
        html = render_to_string('ads/single_item/like_section.html', context, request=request)
        return JsonResponse({'form': html})


@login_required
def favourite_ads(request):
    my_fav_ads = Ad.manager_object.can_be_shown_to_public().filter(likes=request.user).order_by('-creation_date')

    paginator = Paginator(my_fav_ads, 3)
    page = request.GET.get('page')
    try:
        ads = paginator.get_page(page)
    except EmptyPage:
        ads = paginator.get_page(1)
    except PageNotAnInteger:
        ads = paginator.get_page(1)
    context = {
        'my_ads_fav': ads,
        'unlike_ad': unlike_ad
    }

    if request.is_ajax():
        html = render_to_string('ads/favourite/favourite_section.html', context, request=request)
        return JsonResponse({'form': html})

    return render(request, 'ads/favourite/favourite.html', context)


@login_required
def unlike_ad(request):
    try:
        ad = get_object_or_404(Ad, id=request.POST.get('id'))

        ad.likes.remove(request.user)

        my_fav_ads = Ad.manager_object.can_be_shown_to_public().filter(likes=request.user).order_by('-creation_date')

        paginator = Paginator(my_fav_ads, 5)

        if request.is_ajax():
            page = request.POST.get('page')
        else:
            page = request.GET.get('page')

        ads = paginator.get_page(page)

        if request.is_ajax():
            context = {
                'my_ads_fav': ads,
            }
            html = render_to_string('ads/favourite/favourite_section.html', context, request=request)
            return JsonResponse({'form': html})

    except ValidationError:
        raise Http404
    return redirect('ads:favourite_ads')


@login_required
def my_ads(request):
    """
    This function print the first 5 (with paginator) ads of the user with ajax request
    It can handle delete request too
    """
    my_all_ads = []
    ad_deletion = None
    # if an Ad is deleted, check delete_ad views
    if 'ad_deletion' in request.session:
        ad_deletion = request.session['ad_deletion']
        del request.session['ad_deletion']
    try:
        my_all_ads = Ad.manager_object.can_be_shown_to_owner().filter(ad_user__user=request.user).order_by(
            '-creation_date')
        # request.user.adUser.ads.filter(is_deleted=False).order_by('-creation_date')
    except AdUser.DoesNotExist:
        pass

    paginator = Paginator(my_all_ads, 5)
    page = request.GET.get('page')
    try:
        ads = paginator.get_page(page)
    except EmptyPage:
        ads = paginator.get_page(1)
    except PageNotAnInteger:
        ads = paginator.get_page(1)
    if request.is_ajax():
        context = {
            'ads': ads,
        }
        html = render_to_string('ads/my_ads/myAds.html', context, request=request)
        return JsonResponse({'form': html})

    context = {
        'ads': ads,
        'ad_deletion': ad_deletion
    }

    return render(request, 'ads/my_ads/my_ads.html', context)


def delete_ad(request, ad_id=None, random_code=''):
    try:
        ad_to_delete = Ad.objects.get(pk=ad_id, is_deleted=False)
    except Ad.DoesNotExist:
        raise Http404
    else:
        if (request.user == ad_to_delete.ad_user.user) or (
                ad_to_delete.random_code and ad_to_delete.random_code == random_code):
            ad_to_delete.is_deleted = True
            ad_to_delete.is_active = False
            ad_to_delete.save()
            request.session['ad_deletion'] = 'ok'
            if random_code != '':
                return redirect("ads:create_post")

    return redirect("ads:my_ads")


@login_required
def ad_status(request):
    """
     ad_satus function handle whether an ad is active or not
    """
    try:
        ad = get_object_or_404(Ad, id=request.POST.get('id'))
        if request.user == ad.ad_user.user:
            ad.is_active = not ad.is_active
            ad.save()
        my_all_ads = request.user.adUser.ads.filter(is_deleted=False).order_by('-creation_date')
        paginator = Paginator(my_all_ads, 5)

        if request.is_ajax():
            page = request.POST.get('page')
        else:
            page = request.GET.get('page')

        ads = paginator.get_page(page)
        context = {
            'ads': ads
        }
        if request.is_ajax():
            html = render_to_string('ads/my_ads/myAds.html', context, request=request)
            return JsonResponse({'form': html})

    except ValidationError:
        raise Http404
    # return render(request, 'ads/my_ads.html')
    return redirect('ads:my_ads')


@login_required
def my_alerts(request):
    all_categories = Category.objects.filter(category_type="T")
    alert_error = request.session.get('alert_error', None)
    alert_success = request.session.get('alert_success', None)
    id_to_delete = request.GET.get('to_delete', None)
    deletion = False

    if id_to_delete:
        try:
            alert_to_delete = Alert.objects.get(pk=id_to_delete)
        except Alert.DoesNotExist:
            pass
        else:
            if request.user == alert_to_delete.user:
                alert_to_delete.delete()
                deletion = True

    if alert_error:
        del request.session['alert_error']
    if alert_success:
        del request.session['alert_success']
    context = {
        'all_categories': all_categories,
        'alert_error': alert_error,
        'alert_success': alert_success,
        'deletion': deletion

    }
    return render(request, 'ads/my_alerts/my_alerts.html', context)


@login_required
def my_alert_confirmation(request):
    if request.method == "POST":
        email = request.POST['email']
        option = request.POST['radioInline']
        category_id = request.POST['category']
        category = Category.objects.get(id=category_id)

        my_alerts_count = Alert.objects.filter(user=request.user).count()
        if my_alerts_count >= 3:
            request.session['alert_error'] = 'limit_error'
            return redirect('ads:my_alerts')
        try:
            validate_email(email)
        except ValidationError:
            request.session['alert_error'] = 'email_error'
            return redirect('ads:my_alerts')

        same_alert = Alert.objects.filter(user=request.user, email=email, frequency=option, category=category).first()
        if same_alert:
            request.session['alert_error'] = 'same_alert'
            return redirect('ads:my_alerts')

        alert = Alert.objects.create(user=request.user, email=email, frequency=option, category=category)
        alert.save()
        request.session['alert_success'] = 'alert_success'
        return redirect('ads:my_alerts')


@login_required
def feature_ad(request):
    if request.is_ajax:
        ad_id = request.POST.get('id')
        ad = get_object_or_404(Ad, id=ad_id)
        histo_feature = HistoricalFeatured.objects.filter(ad_id=ad.id).first()
        try:
            feature = ad.feature
        except AdFeatured.DoesNotExist:
            feature = AdFeatured(ad=ad)
            feature.save()
            if histo_feature:
                histo_feature.date = timezone.now()
                histo_feature.save()
            else:
                HistoricalFeatured.objects.create(ad_id=ad.id)
        else:
            feature.delete()
            if histo_feature:
                histo_feature.date = timezone.now()
                histo_feature.save()
        html = render_to_string('ads/single_item/feature_section.html', {'ad': ad}, request=request)
        return JsonResponse({'featured': html})


def signal(request, random_url):
    """
    Function that handle the signal of an add by a user 
    """
    if request.method == 'POST':
        signal_type = request.POST['signal']
        try:
            ad = Ad.objects.get(random_url=random_url)
        except Ad.DoesNotExist:
            return Http404
        response = redirect(reverse('ads:single_item', args=(ad.random_url.hex,)))
        cookie_id = "signal_ad_%s" % ad.id
        success = False
        if request.user.is_authenticated:
            signal_ad = ad.signals.filter(user=request.user)
            if not signal_ad and cookie_id not in request.COOKIES:
                Signal.objects.create(user=request.user, ad=ad, type=signal_type)
                response.set_cookie(cookie_id, ad.id)
                success = True
        else:
            if cookie_id not in request.COOKIES:
                Signal.objects.create(ad=ad, type=signal_type)
                response.set_cookie(cookie_id, ad.id)
                success = True

        if success:
            request.session['ad_signal'] = 'ok'
            if ad.signals.count() >= 3:
                ad.on_pause = True
                ad.save()
        else:
            request.session['ad_signal'] = 'already_signaled'
        return response
