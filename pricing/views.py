from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Account, AccountActivation


def pricing(request):
    return render(request, 'pricing/pricing.html')


@login_required
def pricing_activation(request, account_type):
    if not account_type_exists(account_type):
        pass
    return render(request, 'pricing/pricing_activation.html', {'account_type': account_type})


@login_required
def pricing_activation_verification(request, account_type):
    if not account_type_exists(account_type):
        pass

    return render(request, 'pricing/pricing_activation.html', {'account_type': account_type})


def account_type_exists(account_type):
    if account_type in ['NORMAL', 'PROFESSIONAL', 'ADVANCED']:
        return True
    return False
