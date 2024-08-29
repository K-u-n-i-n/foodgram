from django.urls import include, path
from djoser import views as djoser_views
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'', views.UserViewSet, basename='user'),

urlpatterns = [
    path('me/avatar/', views.UserAvatarView.as_view(), name='user-avatar'),
    path('me/', views.UserSelfView.as_view()),
    path(
        'set_password/',
        djoser_views.UserViewSet.as_view({'post': 'set_password'}),
        name='user-set-password'
    ),
    path('', include(router.urls)),
]
