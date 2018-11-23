from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
import video_streaming.routing
from code_reader.consumers import CodeReaderConsumer


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
            URLRouter(
                video_streaming.routing.websocket_urlpatterns
            )
        ),
    'channel': ChannelNameRouter({
        'start-code-reading': CodeReaderConsumer,
    })

})
