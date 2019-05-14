from difflib import SequenceMatcher
from django.utils import timezone
import os
import random
import string


def similar(a, b):
    """ compute the similarity of two string """
    return SequenceMatcher(None, a, b).ratio()


def ads_are_similar(ads_1, ads_2):
    """ If strings ratio is more or equal than 0.5 then it's fine """
    if similar(ads_1, ads_2) >= 0.5:
        return True

    return False


def days_hence(days):
    return timezone.now() + timezone.timedelta(days=days)


def _delete_file(path):
    """ Deletes file from filesystem. """
    os.remove(path)


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
