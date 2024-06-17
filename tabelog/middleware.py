# middleware.py
import datetime
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class RememberMeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated and 'remember' in request.POST:
            max_age = 365 * 24 * 60 * 60  # 1 year
            request.session.set_expiry(max_age)
            response.set_cookie(settings.SESSION_COOKIE_NAME, request.session.session_key, max_age=max_age)
        return response
