from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Account, one_month_hence
from django.urls import reverse
from django.http import Http404
from django.http import HttpResponseNotFound
import paydunya
from django.conf import settings as conf_settings


def pricing(request):
    return render(request, 'pricing/pricing.html')


@login_required
def pricing_activation(request, account_type, token='None'):
    print(token)
    if not account_type_exists(account_type):
        return HttpResponseNotFound("Cette page n'existe pas")
    payment_error = None
    payment_success = None
    if 'payment_error' in request.session:
        payment_error = request.session['payment_error']
        del request.session['payment_error']
    if 'payment_success' in request.session:
        payment_success = request.session['payment_success']
        del request.session['payment_success']
    amount = account_corresponding_payment(account_type)
    return render(request, 'pricing/pricing_activation.html',
                  {'account_type': account_type, 'amount': amount, 'token': token, 'payment_error': payment_error,
                   'payment_success': payment_success})


@login_required
def pricing_activation_verification_1(request, account_type, token='None'):
    if not account_type_exists(account_type):
        return HttpResponseNotFound("Cette page n'existe pas")
    if request.method == "POST":
        email_number = request.POST['email_number']
        try:
            int(email_number)
        except ValueError:
            pass
        else:
            email_number = "+221" + email_number

        amount = account_corresponding_payment(account_type)
        opr_data = {
            'account_alias': email_number,
            'description': "Payment d'un compte " + account_type + " chez Yërël",
            'total_amount': amount
        }
        store = paydunya.Store(name='Yerel')
        conf_settings.OPR[request.user] = paydunya.OPR(opr_data, store)
        successful, response = conf_settings.OPR[request.user].create()
        print(response)
        if successful:
            token = response['token']
            print(token)
        else:
            request.session['payment_error'] = True
            # {'response_code': '00', 'response_text': 'PSR-test_8Odlpj',
            # 'description': 'Onsite Payment Request successfully sent.', 'token': 'PSR-test_8Odlpj',
            # 'invoice_token': 'test_76wcGtD4fF'}

        return redirect(reverse('pricing:activation', args=[account_type, token]))


@login_required
def pricing_activation_verification_2(request, account_type, token):
    if not account_type_exists(account_type):
        return HttpResponseNotFound("Cette page n'existe pas")
    if request.method == "POST":
        code = request.POST['confirmation_code']
        successful, response = conf_settings.OPR[request.user].charge({
            'token': token,
            'confirm_token': code
        })

        if successful:
            try:
                account = Account.objects.get(user=request.user)
            except Account.DoesNotExist:
                Account.objects.create(type=account_type[0], token=token, user=request.user)
            else:
                account.end_date = one_month_hence()
                account.save()
            finally:
                request.session['payment_success'] = True
        else:
            request.session['payment_error'] = True

        return redirect(reverse('pricing:activation', args=(account_type, token,)))


def account_type_exists(account_type):
    if account_type in ['NORMAL', 'PROFESSIONAL', 'ADVANCED']:
        return True
    return False


def account_corresponding_payment(account_type):
    if account_type == 'NORMAL':
        amount = 2000
    elif account_type == 'PROFESSIONAL':
        amount = 7000
    else:
        amount = 15000
    return amount


ACCOUNT_TYPE_WITH_LIMITS = (('NORMAL', 20), ('PROFESSIONAL', 50), ('ADVANCED', None))


def has_exceed_ads_limit(account_type, nb_ads):
    for a_type, limit in ACCOUNT_TYPE_WITH_LIMITS:
        if a_type == account_type and limit == nb_ads:
            return True

    return False
