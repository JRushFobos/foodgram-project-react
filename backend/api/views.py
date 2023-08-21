from rest_framework import viewsets

from recipes.models import Tags
from .serializers import TagsSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
