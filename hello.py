import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

package = 'Hello'

class Greeting(messages.Message):
    """Greeting that stores a message."""
    message = messages.StringField(1)

@endpoints.api(name='helloworldendpoints', version='v1')
class HelloWorldEndPointsApi(remote.Service):
    """HelloWorldEndPoints API v1."""

    @endpoints.method(message_types.VoidMessage, Greeting,
                      path='sayHello', http_method='GET',
                      name='sayHello')
    def sayHello(self, unused_request):
        return Greeting(message="Hello World!")

    ID_RESOURCE = endpoints.ResourceContainer(
            message_types.VoidMessage,
            name=messages.StringField(1))

    @endpoints.method(ID_RESOURCE, Greeting,
                      path='sayHelloByName/{name}', http_method='GET',
                      name='sayHelloByName')
    def sayHelloByName(self, request):
        try:
            return Greeting(message="Hello %s!" % request.name)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Greeting %s not found.' %
                                              (request.name,))

    Period_RESOURCE = endpoints.ResourceContainer(
            message_types.VoidMessage,
            name=messages.StringField(1),
            period=messages.StringField(2))

    @endpoints.method(Period_RESOURCE, Greeting,
                      path='greetByPeriod/{name,period}', http_method='GET',
                      name='greetByPeriod')
    def greetByPeriod(self, request):
        try:
            return Greeting(message="Good %s %s!" % (request.period, request.name))
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Greeting %s not found.' %
                                              (request.name,))

APPLICATION = endpoints.api_server([HelloWorldEndPointsApi])