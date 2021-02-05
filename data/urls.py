from django.urls import path
from .views import sentry_test

urlpatterns = [
    path('test', sentry_test, name='sentry-test'),
]