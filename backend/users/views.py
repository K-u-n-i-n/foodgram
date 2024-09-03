# from django.contrib.auth import get_user_model
# from rest_framework import status
# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.viewsets import ModelViewSet

# from users.models import Subscription
# from .serializers import (
#     AvatarSerializer,
#     SubscriptionSerializer,
#     UserRegistrationSerializer,
#     UserSerializer
# )


# User = get_user_model()


# class UserViewSet(ModelViewSet):
#     permission_classes = (AllowAny,)
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UserRegistrationSerializer
#         return super().get_serializer_class()


# class UserSelfView(APIView):
#     """
#     Представление для получения данных
#     текущего пользователя.

#     Доступно только для аутентифицированных пользователей.
#     """

#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)

#     # def patch(self, request):
#     #     serializer = UserSerializer(
#     #         request.user, data=request.data, partial=True)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return Response(serializer.data)
#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserAvatarView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, *args, **kwargs):
#         user = request.user
#         serializer = AvatarSerializer(user, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({
#             'avatar': request.build_absolute_uri(user.avatar.url)
#         }, status=status.HTTP_200_OK)

#     def delete(self, request, *args, **kwargs):
#         user = request.user
#         user.avatar.delete(save=True)
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class SubscriptionListView(ListAPIView):
#     serializer_class = SubscriptionSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Subscription.objects.filter(user=self.request.user)

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
