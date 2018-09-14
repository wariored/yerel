from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Subcategory
from .serializers import CategorySerializer, SubcategorySerializer
from yeureul_api.our_permissions import IsAdminOrReadOnly

class CategoryList(generics.ListCreateAPIView):
    """
    List all categories, or create a new category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryList(generics.ListCreateAPIView):
    """
    List all subcategories, or create a new subcategory.
    """
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a subcategory.
    """
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

class CategorySubcategories(generics.GenericAPIView):
    """
    Get all subcategories of a category by id
    """
    queryset = Category.objects.all()
    def get(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = SubcategorySerializer(category.categ_subcategs, many=True)
        return Response(serializer.data)
class SubcategoryCategory(generics.GenericAPIView):
    """
    Get the category that a subcategory belong by id
    """
    queryset = Subcategory.objects.all()
    def get(self, request, *args, **kwargs):
        subcategory = self.get_object()
        serializer = CategorySerializer(subcategory.category)
        return Response(serializer.data)





