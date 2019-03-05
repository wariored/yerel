from django_elasticsearch_dsl import DocType, Index, fields
from .models import Ad, Category, AdUser, Location, AdFile
from django.db import models

ads = Index('ads')


@ads.doc_type
class AdDocument(DocType):
    ad_user = fields.NestedField(properties={
        'given_name': fields.StringField(),
    })
    subcategory = fields.NestedField(properties={
        'name': fields.StringField(),
        'sup_category': fields.NestedField(properties={
            'name': fields.StringField()
        })
    })
    location = fields.NestedField(properties={
        'name': fields.StringField(),
    })

    img = fields.ObjectField(properties={
        'media': fields.FileField(),
    })

    random_url = fields.NestedField(properties={
        'hex': fields.StringField(),
    })

    class Meta:
        model = Ad
        related_models = [Category, AdUser, Location, AdFile]

        fields = [
            'id',
            'creation_date',
            'title',
            'price',
            'description',
            'condition',
        ]

    # def get_instances_from_related(self, tag_instance):
    #   return tag_instance.ad_set.all()
