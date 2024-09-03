from django.urls import include, path
from djoser import views as djoser_views
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'users/', views.UserViewSet, basename='user'),
router.register(r'tags/', views.TagViewSet),
router.register(r'recipes/', views.RecipeViewSet),
router.register(r'ingredients/', views.IngredientViewSet),


urlpatterns = [
    path(
        'auth/', include('djoser.urls.authtoken')
    ),
    path(
        'users/me/avatar/', views.UserAvatarView.as_view(), name='user-avatar'
    ),
    path(
        'users/me/', views.UserSelfView.as_view()
    ),
    path(
        'users/set_password/',
        djoser_views.UserViewSet.as_view({'post': 'set_password'}),
        name='user-set-password'
    ),
    path('', include(router.urls)),
]
