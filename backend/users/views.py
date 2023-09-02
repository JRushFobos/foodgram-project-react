from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from api.paginations import PageNumberPagination
from .serializers import SubscriptionSerializer, CheckSubscriptionSerializer

User = get_user_model()


class UserViewSet(UserViewSet):
    """Вью сет пользователей и подписок."""

    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=("get",),
        serializer_class=SubscriptionSerializer,
    )
    def subscriptions(self, request):
        """Получение списка польвателей"""
        user = self.request.user
        user_subscriptions = user.subscribes.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        serializer_class=SubscriptionSerializer,
    )
    def subscribe(self, request, id=None):
        """Создание и удаление подписок."""
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        data = {
            "user": user.id,
            "author": author.id,
        }

        if self.request.method == "POST":
            serializer = CheckSubscriptionSerializer(
                data=data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            result = Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                result, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            serializer = CheckSubscriptionSerializer(
                data=data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            user.subscribes.filter(author=author).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
