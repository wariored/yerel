from difflib import SequenceMatcher


# This fonction allow to compute the similariry of two string
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def ads_are_similar(ads_1, ads_2):
    if similar(ads_1, ads_2) >= 0.5:
        return True

    return False
