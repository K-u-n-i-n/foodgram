import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Поле сериализатора для обработки изображений,
    закодированных в формате Base64.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            img_data = base64.b64decode(imgstr)

            file_name = f'{uuid.uuid4()}.{ext}'

            if not imghdr.what(None, img_data):
                raise serializers.ValidationError('Неверное изображение')

            data = ContentFile(img_data, name=file_name)

        return super().to_internal_value(data)
