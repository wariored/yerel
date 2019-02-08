from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Ad, AdUser, AdFile, Location
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings as conf_settings
from django.utils import timezone
from PIL import Image
from django.http import Http404 , JsonResponse
from django.urls import reverse
import uuid
from django.template.loader import render_to_string


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
        if request.user.is_authenticated:
            if request.user.account:
                if request.user.account.is_active():
                    pass
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
            if len(photos) > 5:
                request.session['create_post_error'] = 'photos'
                request.session['dict_values'] = dict_values
                return redirect('ads:create_post')
            check_photos = ['error' for p in photos if p.size > int(conf_settings.MAX_UPLOAD_SIZE)]
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
            ad_user = AdUser.objects.create(given_name=name, phone_number=phone_number, email=email)
        else:
            user = request.user
            given_name = user.first_name + ' ' + user.last_name
            ad_user = AdUser.objects.create(user=user, email=user.email, given_name=given_name, phone_number=user.info.phone_number)
        subcategory = Category.objects.get(pk=category)
        location = Location.objects.get(pk=location)
        ad = Ad.objects.create(title=title, price=price, condition=condition, description=description,
                               subcategory=subcategory, location=location, ad_user=ad_user, creation_date=timezone.now()
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


def single_item(request, random_url):
    try:
        random_url = uuid.UUID(random_url)
        ad = Ad.objects.get(random_url=random_url)
        if not request.session.get('viewed_post_%s' % id , False):
            ad.views_number += 1
            ad.save()
            request.session['viewed_post_%s' % id] = True
        count = ad.likes.count()
    except ValidationError:
        raise Http404
    return render(request, 'ads/single_item.html', {'ad': ad , 'like_count':count })
    #if request.user.is_authenticated:


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

def like_post(request):
    ad = get_object_or_404(Ad , id=request.POST.get('id'))
    if request.user in ad.likes.all():
        ad.likes.remove(request.user)
    else:
        ad.likes.add(request.user)

    count = ad.likes.count()
    context = {
        'like_count':count , 
        'ad': ad,
    }
    if  request.is_ajax(): 
        html = render_to_string('ads/like_section.html' , context , request=request)
        return JsonResponse({'form':html})