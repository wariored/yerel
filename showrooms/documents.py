from django_elasticsearch_dsl import DocType, Index
from .models import Showroom

showrooms = Index('showrooms')


@showrooms.doc_type
class ShowroomDocument(DocType):

    class Meta:
        model = Showroom

        fields = [
            'id',
            'name',
            'email',
            'website',
            'description'
        ]
