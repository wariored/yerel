from rest_framework import viewsets
from .models import Category, Subcategory
from .serializers import CategorySerializer, SubcategorySerializer

# ViewSets define the view behavior.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer