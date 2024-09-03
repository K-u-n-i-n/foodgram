# from django.contrib.auth import get_user_model
# from rest_framework import serializers

# from backend.api.serializers import Base64ImageField
# from recipes.models import Recipe
# from recipes.serializers import RecipeSerializer
# from users.models import Subscription


# User = get_user_model()


# class UserRegistrationSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=True)
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name', 'last_name', 'password'
#         )
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def create(self, validated_data):
#         return User.objects.create_user(**validated_data)


# class UserSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name',
#             'last_name', 'is_subscribed', 'avatar'
#         )

#     def get_is_subscribed(self, obj):
#         # Проверить наличие подписки в другой таблице
#         return False


# class AvatarSerializer(serializers.ModelSerializer):
#     avatar = Base64ImageField(max_length=None, use_url=True)

#     class Meta:
#         model = User
#         fields = ['avatar']


# class SubscriptionSerializer(serializers.ModelSerializer):
#     recipes = RecipeSerializer(
#         many=True, read_only=True, source='author.recipe_set'
#     )
#     recipes_count = serializers.SerializerMethodField()
#     avatar = AvatarSerializer(read_only=True)

#     class Meta:
#         model = Subscription
#         fields = (
#             'email', 'id', 'username', 'first_name', 'last_name',
#             'is_subscribed', 'recipes', 'recipes_count', 'avatar'
#         )

#     def get_recipes_count(self, obj):
#         return Recipe.objects.filter(author=obj.author).count()

#     # def get_avatar(self, obj):
#     #     return obj.author.profile.avatar.url if hasattr(obj.author, 'profile') else None
