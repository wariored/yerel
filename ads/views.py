import uuid

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import validate_email
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from ads.forms import AdForm
from yeureul import statics_variables
from yeureul.utils_functions import ads_are_similar

from .forms import AdForm
from .models import Ad, AdFile, AdUser, Category, Location


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
            except AdUser.DoesNotFound:
                ad_user = AdUser.objects.create(given_name=name, phone_number=phone_number, email=email) 
        else:
            user = request.user
            given_name = user.first_name + ' ' + user.last_name
            try:
                ad_user = AdUser.objects.get(email=user.email)
            except AdUser.DoesNotFound:
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

@transaction.atomic
def update_post_verification(request):
    pass

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
        all_ads = Ad.objects.all().exclude(pk=ad.pk)
        print("This is the add : ", ad.ad_user.user)   
        for add in all_ads:
            if ads_are_similar(add.description, ad.description):
                similar_ads.append(add)

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

'''
This function print the first 5 ads of the user 
'''
@login_required
def my_ads(request, page=1):    
    myAds = [aduser.ads.all().exclude(is_deleted = True).first()
                for aduser in request.user.aduser.all()
                if len(aduser.ads.all().exclude(is_deleted = True))!=0]
    
    paginator = Paginator(myAds, 1)
    # page = request.GET.get('page')
    print(page)
    # ads = paginator.page(1)
    try:
        ads = paginator.get_page(page)
    except EmptyPage:
        ads = paginator.get_page(1)
    except PageNotAnInteger:
        ads = paginator.get_page(1)
    context = {
        'ads': ads
    }
    
    if request.is_ajax():
        html = render_to_string('ads/myAds.html', context, request=request)
        return JsonResponse({'form': html})
    else:
        return render(request, 'ads/my_ads.html', context)

# 


'''
Handle the update of a ad by the aduser 
'''
@login_required
def update_ad(request, random_url):
    try:
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        form = AdForm(request.POST or None , instance=ad)
        if form.is_valid():
            form.save()
            return render(request, 'ads/single_item.html', {'ad': ad})
        context = {
            'form':form,
            'ad':ad
        }
    except ValidationError:
        raise Http404    
    return render(request, 'ads/update_post.html', context)

@login_required
def delete_ad (request, random_url):
    try:
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        delete_confirmation = False 
        if request.method == "GET":
            delete_confirmation = True
    
        if request.method == "POST":
            validation = request.POST['validation']
            if validation == 'Confirmer':
                ad.is_deleted = True
                ad.save()
                print("deleted welll")
            else:
                pass
            return redirect('ads:my_ads')
        context = {
        'delete_confirmation':delete_confirmation
        }
    except ValidationError:
        raise Http404
    return render(request, 'ads/my_ads.html', context)


'''
 ad_satus function handle whether a ad is active or not 
'''
@login_required
def ad_status(request, random_url):
    try:
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        ad.is_active = not ad.is_active 
        ad.save()
    except ValidationError:
        raise Http404
    # return render(request, 'ads/my_ads.html')
    return redirect('ads:my_ads')

@login_required
def my_alerts(request):
    return render(request, 'ads/my_alerts.html')
