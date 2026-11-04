from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_id=serializers.PrimaryKeyRelatedField(source='parent',queryset=Category.objects.all(),required=False,allow_null=True)
    class Meta:
        model = Category
        fields = ["id", "name", "parent_id"]
