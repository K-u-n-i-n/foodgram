from recipes.models import Subscription


class IsSubscribedMixin:
    """
    Миксин для проверки подписки пользователя на автора.
    """

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request and hasattr(
            request, 'user'
        ) and request.user.is_authenticated:

            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()

        return False
