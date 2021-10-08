from django.urls import re_path
from .consumers import OrderWS

ws_urlpatterns = [
    re_path('order/', OrderWS.as_asgi())
]
