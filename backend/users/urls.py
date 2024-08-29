from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'', views.UserViewSet, basename='user'),

urlpatterns = router.urls
