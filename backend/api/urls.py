from rest_framework.routers import DefaultRouter
from django.urls import include, path

from users.views import UserViewSet
from api.views import IngredientsViewSet, TagsViewSet, RecipesViewSet

app_name = "api"

router_v1 = DefaultRouter()

router_v1.register("users", UserViewSet, basename="users")
router_v1.register("tags", TagsViewSet, basename="tags")
router_v1.register("ingredients", IngredientsViewSet, basename="ingredients")
router_v1.register('recipes', RecipesViewSet, basename="recipes")

urlpatterns = [
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
