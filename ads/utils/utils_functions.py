from yeureul.utils_functions import random_string_generator


def unique_ad_random_code_generator(instance):
    random_code = random_string_generator()

    Klass = instance.__class__

    qs_exists = Klass.objects.filter(random_code=random_code).exists()
    if qs_exists:
        return unique_ad_random_code_generator(instance)
    return random_code
