"""
ASGI config for chatbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import re_path

from chat.consumers import ChatConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatbot.settings")
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket":
            AllowedHostsOriginValidator(
                # WebSocketJWTAuthMiddleWare(
                URLRouter([re_path(r"chat/(?P<room_id>\w+)/$", ChatConsumer.as_asgi())])
                # )
            )
    }
)
