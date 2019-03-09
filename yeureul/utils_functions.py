from difflib import SequenceMatcher
from django.utils import timezone
import os


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
