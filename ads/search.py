from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Search
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models

connections.create_connection()


class AdIndex(DocType):
    ad_user = Text()
    creation_date = Date()
    title = Text()
    price = Text()
    description = Text()
    condition = Text()
    location = Text()
    subcategory = Text()

    class Index:
        name = 'ad_index'


def bulk_indexing():
        AdIndex.init()
        es = Elasticsearch()
        bulk(client=es, actions=(b.indexing() for b in models.Ad.objects.all().iterator()))


def search(title):
    s = Search().filter('term', title=title)
    response = s.execute()
    return response




