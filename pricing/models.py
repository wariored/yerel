from django.db import models


PRICING_TYPE = (
    ('N', 'NORMAL'),
    ('A', 'ADVANCED'),
    ('P', 'PROFESSIONAL')
)

class Pricing(models.Model):
    pass
