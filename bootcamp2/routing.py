from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# from bootcamp2.recommend.view import get_stutus
from .consumers import RecommendStatus


application = ProtocolTypeRouter({

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter([

            path('recommend_status/', RecommendStatus),
            # path("chart/push", MyConsumer),
        ])
    ),
})
