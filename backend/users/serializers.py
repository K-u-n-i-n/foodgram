# import base64
# import imghdr
# import uuid

from django.contrib.auth import get_user_model
# from django.core.files.base import ContentFile
from rest_framework import serializers

from core.serializers import Base64ImageField


User = get_user_model()


# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             img_data = base64.b64decode(imgstr)

#             file_name = f"{uuid.uuid4()}.{ext}"

#             if not imghdr.what(None, img_data):
#                 raise serializers.ValidationError('Неверное изображение')

#             data = ContentFile(img_data, name=file_name)

#         return super().to_internal_value(data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        # Проверить наличие подписки в другой таблице
        return False


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = User
        fields = ['avatar']
