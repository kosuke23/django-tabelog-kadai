from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(mail_address=settings.SUPERUSER_EMAIL).exists():
            User.objects.create_superuser(
                mail_address=settings.SUPERUSER_EMAIL,
                password=settings.SUPERUSER_PASSWORD,
                name=settings.SUPERUSER_NAME
            )
            print("スーパーユーザー作成")