from rest_framework import serializers

from recipes.models import Tags


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'
