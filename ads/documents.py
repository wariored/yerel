from django_elasticsearch_dsl import DocType, Index, fields
from .models import Ad, Category, AdUser, Location, AdFile
from django.db import models

ads = Index('ads')


@ads.doc_type
class AdDocument(DocType):
    # ad_user = fields.NestedField(properties={
    #     'given_name': fields.StringField(),
    # })
    # subcategory = fields.NestedField(properties={
    #     'name': fields.StringField(),
    #     'sup_category': fields.NestedField(properties={
    #         'name': fields.StringField()
    #     })
    # })
    # location = fields.NestedField(properties={
    #     'name': fields.StringField(),
    # })
    #
    # img = fields.ObjectField(properties={
    #     'media': fields.FileField(),
    # })
    #
    # random_url = fields.NestedField(properties={
    #     'hex': fields.StringField(),
    # })

    class Meta:
        model = Ad
        # related_models = [Category, AdUser, Location, AdFile]

        fields = [
            'id',
            'creation_date',
            'title',
            'price',
            'description',
            'condition',
        ]

    # def get_instances_from_related(self, tag_instance):
    #
    #     """If related_models is set, define how to retrieve the instance(s) from the related model.
    #     The related_models option should be used with caution because it can lead in the index
    #     to the updating of a lot of items.
    #     """
    #     if isinstance(tag_instance, Category):
    #         return tag_instance.subcateg_ads.all()
    #     elif isinstance(tag_instance, AdUser):
    #         return tag_instance.ads.all()
    #     elif isinstance(tag_instance, Location):
    #         return tag_instance.loc_ads.all()
    #     elif isinstance(tag_instance, AdFile):
    #         return tag_instance.ad
