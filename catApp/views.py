from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from.models import Category
from .serializers import CategorySerializer
# Create your views here.

class CategoryAPI(APIView):
    def get(self,request):
        name=request.GET.get('name')
        if name:
            category=get_object_or_404(Category,name__iexact=name.strip())
            if category.parent:
                parent={
                    "id":category.parent.id,
                    "name":category.parent.name
                }
            else:
                parent=None

            children=category.subcategories.all()
            subcategories=[]
            for child in children:
                subcategories.append({
                    "id":child.id,
                    "name":child.name
                })
            data={
                "category":{
                    "id":category.id,
                    "name":category.name
                },
                "parent":parent,
                "subcategories":subcategories
            }
            return Response(data,status=status.HTTP_200_OK)

        categories = Category.objects.all().order_by('id')
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit')
        page_size = request.GET.get('page_size', 10)

        if limit:
            page_size = limit
        try:
            page_size = int(page_size)
            if page_size < 1:
                raise ValueError

        except ValueError:
            return Response(
                {"error": "Page size must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )


        paginator = Paginator(categories, page_size)
        page_obj = paginator.get_page(page)
        serializer = CategorySerializer(page_obj.object_list,many=True)
        data = {
            "page": page_obj.number,
            "page_size": page_size,
            "total_count": paginator.count,
            "results": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)



    def post(self, request):
        if isinstance(request.data, list):
            serializer = CategorySerializer(data=request.data,many=True)
        else:
            serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "Category name already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
