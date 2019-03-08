from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import validate_email
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

from .forms import AdForm
from .models import Ad, AdFile, AdUser, Category, Location, HistoricalFeatured, AdFeatured, Alert


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
    if create_post_error:
        del request.session['create_post_error']
        if create_post_error != 'has_reached_limit':
            del request.session['dict_values']
    elif create_post_success:
        del request.session['create_post_success']
    return render(request, 'ads/create_post.html',
                  dict(categories_t=categories_t, locations=locations, create_post_error=create_post_error,
                       create_post_success=create_post_success, dict_values=dict_values
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

        # check if user has reached ads limit
        if request.user.is_authenticated:
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
        if not price or len(price) > 30:
            request.session['create_post_error'] = 'price'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')
        else:
            try:
                float(price)
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
        if not description or len(description) > 2000:
            request.session['create_post_error'] = 'description'
            request.session['dict_values'] = dict_values
            return redirect('ads:create_post')
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
            user = request.user
            given_name = user.first_name + ' ' + user.last_name
            try:
                ad_user = AdUser.objects.get(email=user.email)
            except AdUser.DoesNotExist:
                ad_user = AdUser.objects.create(user=user, email=user.email, given_name=given_name,
                                                phone_number=user.info.phone_number)
        subcategory = Category.objects.get(pk=category)
        location = Location.objects.get(pk=location)
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
        # end transaction, save into DB
        transaction.savepoint_commit(sid)
        # return redirect('ads:single_item', args='')
        request.session['create_post_success'] = 'success'
    return redirect('ads:create_post')


@login_required
def update_ad(request, random_url):
    """
    Handle the update of a ad by the aduser
    """
    try:
        if type(random_url) == str:
            random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        categories = Category.objects.filter(category_type='T')
        locations = Location.objects.all()
        update_ad_error = request.session.get('update_ad_error', None)
        if update_ad_error:
            del request.session['update_ad_error']
        context = {
            'ad': ad,
            'categories_t': categories,
            'locations': locations,
            'update_ad_error': update_ad_error
        }
    except ValidationError:
        raise Http404
    return render(request, 'ads/update_post.html', context)


@transaction.atomic
def update_ad_verification(request, random_url):
    if request.method == 'POST':
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        images = AdFile.objects.filter(ad=ad)
        category = request.POST['category']
        condition = request.POST['condition']
        price = request.POST['price']
        photos = request.FILES.getlist('photos', None)
        location = request.POST['location']
        description = request.POST['description']

        if not price or len(price) > 30:
            request.session['update_ad_error'] = 'price'
            return redirect(reverse('ads:update_ad', args=(ad.random_url.hex,)))
        
        if not description or len(description) > 2000:
            request.session['update_ad_error'] = 'description'
            print("OK")
            return redirect(reverse('ads:update_ad', args=(ad.random_url.hex,)))
        
        if photos:
            if len(photos) > statics_variables.MAX_PHOTOS:
                request.session['update_ad_error'] = 'photos'
                return redirect(reverse('ads:update_ad', args=(ad.random_url.hex,)))
            check_phexiotos = ['error' for p in photos if p.size > int(statics_variables.MAX_SIZE)]
            if 'error' in check_photos:
                request.session['update_ad_error'] = 'photos'
                return redirect(reverse('ads:update_ad', args=(ad.random_url.hex,)))
        if photos:
            images.delete()
            for photo in photos:
                try:
                    Image.open(photo)
                    AdFile.objects.create(ad=ad, media=photo)
                except:
                    request.session['create_post_error'] = 'photo_format'
                    return redirect(reverse('ads:update_ad', args=(ad.random_url.hex,)))

        ad.description = description
        ad.price = price
        ad.condition = condition
        ad.subcategory = Category.objects.get(pk=category)
        ad.location = Location.objects.get(pk=location)
        ad.save()
        return redirect(reverse('ads:single_item', args=(ad.random_url.hex,)))


def single_item(request, random_url):
    try:
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
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
        all_ads = Ad.objects.all().exclude(pk=ad.pk).order_by('-update_date')
        for add in all_ads:
            if ads_are_similar(add.description, ad.description):
                similar_ads.append(add)
                if len(similar_ads) == 6:
                    break

        count = ad.likes.count()
        context = {
            'like_count': count,
            'ad_liked': liked,
            'ad': ad,
            'ads_similar': similar_ads,
        }
    except ValidationError:
        raise Http404

    return render(request, 'ads/single_item.html', context)


def single_item_update(request, random_url):
    try:
        ad = Ad.objects.get(random_url=random_url)
    except ValidationError:
        raise Http404
    return render(request, 'ads/single_item.html', {'ad': ad})


def single_item_delete(request, random_url):
    try:
        ad = Ad.objects.get(random_url=random_url)
    except ValidationError:
        raise Http404
    return render(request, 'ads/single_item.html')


def categories_grid(request):
    return render(request, 'ads/categories_pages/categories_grid.html')


# handle the ad's like
@login_required
def like_ad(request):
    ad = get_object_or_404(Ad, id=request.POST.get('id'))
    # liked = False
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
        html = render_to_string('ads/like_section.html', context, request=request)
        return JsonResponse({'form': html})


@login_required
def favourite_ads(request):
    return render(request, 'ads/favourite.html')


@login_required
def my_ads(request):
    """
    This function print the first 5 ads of the user with ajax request
    It can handle delete request too
    """
    my_all_ads = []
    ad_deletion = None
    # if an Ad is deleted, check delete_ad views
    if 'ad_deletion' in request.session:
        ad_deletion = request.session['ad_deletion']
        del request.session['ad_deletion']
    try:
        my_all_ads = request.user.adUser.ads.filter(is_deleted=False).order_by('-creation_date')
    except AdUser.DoesNotExist:
        pass

    paginator = Paginator(my_all_ads, 5)
    page = request.GET.get('page')
def ad_status(request):
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
        html = render_to_string('ads/myAds.html', context, request=request)
        return JsonResponse({'form': html})

    context = {
        'ads': ads,
        'ad_deletion': ad_deletion
    }

    return render(request, 'ads/my_ads.html', context)


@login_required
def delete_ad(request, ad_id=None):
    try:
        ad_to_delete = Ad.objects.get(pk=ad_id, is_deleted=False)
    except Ad.DoesNotExist:
        raise Http404
    else:
        if request.user == ad_to_delete.ad_user.user:
            ad_to_delete.is_deleted = True
            ad_to_delete.is_active = False
            ad_to_delete.save()
            request.session['ad_deletion'] = 'ok'

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
            html = render_to_string('ads/myAds.html', context, request=request)
            return JsonResponse({'form': html})

    except ValidationError:
        raise Http404
    # return render(request, 'ads/my_ads.html')
    return redirect('ads:my_ads')


@login_required 
def my_alerts(request):
    try:
        my_alert = Alert.objects.filter(user=request.user).last()
    except:
        my_alert = None
    all_categories = Category.objects.filter(category_type = "T")
    email_error_session = request.session.get('email_error', None)
    alert_success = request.session.get('alert_success',None)
    
    if email_error_session :
        del request.session['email_error']     
    if alert_success:
        del request.session['alert_success']
    context = {
        'all_categories': all_categories, 
        'my_alert': my_alert ,
        'email_error':  email_error_session,
        'alert_success':alert_success
    }
    return render(request, 'ads/my_alerts.html', context)

def my_alert_confirmation(request):
     if request.method == "POST":
        email = request.POST['email']
        option = request.POST['radioInline']
        category_id = request.POST['category']
        category = Category.objects.get(id=category_id)
        try:
            validate_email(email)
        except:
            print("ok")
            request.session['email_error'] = 'email_error'
            return redirect('ads:my_alerts') 
        
        alert = Alert.objects.create(user = request.user, email = email, frequency = option, category = category )
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
        html = render_to_string('ads/feature_section.html', {'ad': ad}, request=request)
        return JsonResponse({'featured': html})
