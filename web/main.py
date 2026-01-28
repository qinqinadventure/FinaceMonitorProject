import os
import sys
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import JsonResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application

# 配置Django设置
settings.configure(
    DEBUG=True,
    SECRET_KEY='secret',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    INSTALLED_APPS=[],
    MIDDLEWARE=[],
)

def hello(request):
    return JsonResponse({'message': 'Hello, Django!'})

urlpatterns = [
    path('', hello),
]

application = get_wsgi_application()

if __name__ == '__main__':
    execute_from_command_line(sys.argv)