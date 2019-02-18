from difflib import SequenceMatcher

# This fonction allow to compute the similariry of two string 
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()